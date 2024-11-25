import asyncio
from src.database.access_mssql import AccessMsSQL
from models.query_generator import QueryGenerator
from models.response_generator import ResponseGenerator
from models.sql_corrector import QueryCorrector
from models.query_executor import QueryExecutor
from config.config import settings

class SqlConnector:
    def __init__(self, username: str, password: str, driver: str, server: str):
        self.db_connection = AccessMsSQL(username=username, password=password, db_driver=driver, db_server=server)

    async def get_connection_string(self) -> str:
        return await self.db_connection.main()

async def generate_sql(user_query: str, table_schema: str) -> str:
    query_generator = QueryGenerator(query_template=settings.query.QUERY_TEMPLATE)
    return await query_generator.generate_graph_query(
        user_query=user_query,
        table_schema=table_schema,
    )

async def correct_and_execute_graph(connection_string: str, graph_query: str, user_query: str):
    # Correct the SQL query
    query_corrector = QueryCorrector(
        query_template=settings.sql_correction.CORRECT_TABLE_COLUMN_TEMPLATE
    )
    sql_corrector_chain = await query_corrector.graph_query_corrector()

    # Execute the corrected query
    sql_executor = QueryExecutor(correction_chain=sql_corrector_chain)
    graph_output, graph_query = await sql_executor.run_sql_with_correction(
        connection=connection_string,
        graph_query=graph_query,
        extra_context={
            "question": user_query,
            "dialect": "MsSQL",
            "schema": settings.boundplatform.BOUNDPLATFORM_SCHEMA,
        },
    )
    return graph_output

async def generate_response(user_query: str, history: list, graph_output: str) -> str:
    response_generator_chain = ResponseGenerator(
        settings.response_generation.FINAL_RESPONSE_GENERATION_PROMPT
    )
    return await response_generator_chain.response_generator(user_query, history, graph_output)

async def main():
    # Prepare the database connection
    sql_connector = SqlConnector(
        username=settings.mssql.USERNAME,
        password=settings.mssql.PASSWORD,
        driver=settings.mssql.DRIVER,
        server=settings.mssql.SERVER
    )
    connection_string = await sql_connector.get_connection_string()

    # User query and schema
    user_query = "What is the OsType name for Windows?"
    table_schema = settings.boundplatform.BOUNDPLATFORM_SCHEMA

    # Generate SQL query from user query
    graph_query = await generate_sql(user_query, table_schema)

    # Execute the SQL query and retrieve the results
    graph_output = await correct_and_execute_graph(connection_string, graph_query, user_query)

    # Generate final response based on the results
    history = [{"Human": "Hello", "AI": "How may I help you?"}]
    final_output = await generate_response(user_query, history, graph_output)

    # Print the final output
    print(final_output)

if __name__ == "__main__":
    # Run the optimized asynchronous main function
    asyncio.run(main())