import urllib.parse
from neo4j import GraphDatabase

def create_sqlalchemy_url(
    username: str, password: str, driver: str, server: str
) -> str:
    """
    Create the SQLAlchemy connection string.

    Args:
        username (str): The username for database authentication.
        password (str): The password for database authentication.
        driver (str): The ODBC driver for SQL Server.
        server (str): The database server address.

    Returns:
        str: The SQLAlchemy connection string.
    """
    try:
        database_cred = (
            f"Driver={driver};"
            f"Server={server};"
            f"UID={username};"
            f"PWD={password};"
        )
        params = urllib.parse.quote_plus(database_cred)
        sqlalchemy_url = f"mssql+pyodbc:///?odbc_connect={params}"
        return sqlalchemy_url
    except Exception:
        return ""

