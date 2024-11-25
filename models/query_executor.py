import pandas as pd
from typing import Tuple
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from decorators.retry_decorators import retry_on_failure
from utils.query_static.query_utils import clean_llm_sql


class QueryExecutor:
    """
    Updates a SQL Query based on error message and reruns

    Flow:
        - Runs Query - function
        - Encounters error
        - Launches Prompt
    """

    def __init__(self, correction_chain):
        self.sql_correct_chain = correction_chain

    async def run_sql_with_correction(self, connection, graph_query: str, **kwargs):
        """
        Execute the sql, Try to connect the SQL upto `self.attempts` times upon failure.
        """

        error_history = {}
        count = 0

        # Initial attempt, retry logic handled in the run_sql_query decorator
        status, result = await run_sql_query(
            connection_string=connection, graph_query=graph_query
        )

        while not status:
            error_history[f"attempt_{count}"] = (result, graph_query)

            # Run the correction chain and update the SQL query
            graph_query = await self.llm_correction(error_history, count, **kwargs)
            count += 1
            status, result = await run_sql_query(
                connection_string=connection, graph_query=graph_query
            )

        return result, graph_query
        # Run SQL connection chain and update the SQL query

    async def llm_correction(self, error_history, attempt_count, **kwargs):
        correction_context = kwargs.get("extra_context", {})
        error_msg, errored_query = error_history[f"attempt_{attempt_count}"]

        correction_context["suggestions"] = str(error_msg["error"])
        correction_context["prev_query"] = errored_query

        corrected_sql = await self.sql_correct_chain.ainvoke(correction_context)
        corrected_sql = clean_llm_sql(corrected_sql)
        return corrected_sql


@retry_on_failure(max_retries=3, delay=1)
async def run_sql_query(connection_string: str, graph_query: str) -> Tuple[bool, dict]:
    status = False
    output = None
    print("Running SQL query")

    try:
        # Create SQLAlchemy engine and connect to the database
        engine = create_engine(connection_string)

        # Execute the query using a connection context
        with engine.connect() as connection:
            # Execute the query
            result = connection.execute(text(graph_query))

            # Fetch all results as a list of dictionaries
            results = result.mappings().all()

            if results:
                # Convert results into a pandas DataFrame
                df = pd.DataFrame(results)
                # Convert the DataFrame to a dictionary
                output = df.to_dict("list")
                status = True
            else:
                output = {"error": "No data returned from the query."}

    except SQLAlchemyError as e:
        # Handle SQLAlchemy-related errors
        print(f"An error occurred: {e}")
        output = {"error": str(e)}

    return status, output
