from core.chains import create_query_chain
from utils.query_static.query_utils import clean_llm_sql


class QueryGenerator:
    """
    A class to handle SQL Query generation from natural language input
    """

    def __init__(self, query_template: str):
        """
        Initialize the SQLGenerator class by creating the SQL Generation chain

        Args:
            query_template (str): A prompt template to generate SQL queries
        """
        self.query_template = query_template
        self.query_chain = None

    async def initialize_chain(self):
        """
        Initialize the chain for SQL Generation
        """
        self.query_chain = await create_query_chain(
            self.query_template,
            input_variables=[
                "question",
                "dialect",
                "schema",
                "examples_sample_rows",
                "table_name",
                "column_info",
            ],
        )

    async def generate_graph_query(
        self,
        user_query: str,
        table_schema: str,
        dialect: str = "MsSQL",
    ):
        """
        Generate an SQL query from the user query and table schema

        Args:
            user_query (str): The user query
            table_schema (str): The schema of the table
            dialect (str): The SQL dialect to be used

        Returns:
            str: The generated SQL query
        """

        # Ensure the chain  is initialized
        if not self.query_chain:
            await self.initialize_chain()

        # Invoke the query generation chain asynchronously
        sql_query = await self.query_chain.ainvoke(
            {
                "question": user_query,
                "dialect": dialect,
                "schema": table_schema,
            }
        )
        

        # Clean the geneerated SQL query before returning
        clean_sql_query = clean_llm_sql(sql_query)

        return clean_sql_query
