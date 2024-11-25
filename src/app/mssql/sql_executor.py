import pandas as pd
from typing import Tuple, Generator
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from config.config import settings
from src.database.access_mssql import AccessMsSQL
 
async def run_sql_query_in_batches(connection_string: str, sql_query: str, batch_size: int):
    offset = 0
    status = False
 
    try:
        # Create SQLAlchemy engine and connect to the database
        engine = create_engine(connection_string)
 
        while True:
            # Modify the SQL query to use OFFSET and FETCH NEXT for batching
            paginated_query = f"{sql_query} ORDER BY (SELECT NULL) OFFSET {offset} ROWS FETCH NEXT {batch_size} ROWS ONLY"
            print(paginated_query)
            with engine.connect() as connection:
                # Execute the paginated query
                result = connection.execute(text(paginated_query))
 
                # Fetch batch results as a list of dictionaries
                results = result.mappings().all()
 
                if not results:
                    break  # Exit if no more results in batch
 
                # Convert results into a pandas DataFrame
                df = pd.DataFrame(results)
                status = True
                yield status, df  # Yield each batch
 
                # Update offset for next batch
                offset += batch_size
 
    except SQLAlchemyError as e:
        # Handle SQLAlchemy-related errors
        print(f"An error occurred: {e}")
        yield status, pd.DataFrame()
 
 
async def run_sql_query(connection_string: str, sql_query: str) -> Tuple[bool, dict]:
    status = False
    output = None
    print("Running SQL query")

    try:
        # Create SQLAlchemy engine and connect to the database
        engine = create_engine(connection_string)

        # Execute the query using a connection context
        with engine.connect() as connection:
            # Execute the query
            result = connection.execute(text(sql_query))

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

class SqlConnector:
    def __init__(self, username: str, password: str, driver: str, server: str):
        self.db_connection = AccessMsSQL(username=username, password=password, db_driver=driver, db_server=server)
 
    async def get_connection_string(self) -> str:
        return await self.db_connection.main()
 
async def main():
    sql_connector = SqlConnector(
        username=settings.mssql.USERNAME,
        password=settings.mssql.PASSWORD,
        driver=settings.mssql.DRIVER,
        server=settings.mssql.SERVER
    )
    connection_string = await sql_connector.get_connection_string()
    sql_query = 'SELECT BoundPlatformOSId,  BoundPlatformOSSoftwareLimitsId, DataClass,  DataReleaseLevel,  LimitValue  FROM dbo.BoundPlatformOSSoftwareLimits'  # Replace with your actual table name
    success, output_df = await run_sql_query(connection_string=connection_string, sql_query=sql_query)
    return success, output_df

if __name__ == "__main__":
    import asyncio
    status,  output = asyncio.run(main())