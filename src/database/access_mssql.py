from typing import Optional

from .base import DatabaseConnector
from utils.db_utils import create_sqlalchemy_url


class AccessMsSQL(DatabaseConnector):
    def __init__(self, username: str, password: str, db_driver: str, db_server: str):
        """
        Initialize the AccessMsSQL object with the provided username, password, driver, and server.

        Args:
            username (str): The username for database authentication.
            password (str): The password for database authentication.
            db_driver (str): The ODBC driver for SQL Server.
            db_server (str): The database server address.
        """
        self.username = username
        self.password = password
        self.db_driver = db_driver
        self.db_server = db_server

    async def connect_to_database(self) -> str:
        """
        Connect to the database and generate the SQLAlchemy connection string.

        Returns:
            str: The SQLAlchemy connection string for accessing the database.
        """
        return create_sqlalchemy_url(
            self.username, self.password, self.db_driver, self.db_server
        )

    async def main(self) -> Optional[str]:
        """
        Connect to the database and return the SQLAlchemy connection string.

        Returns:
            str or None: The SQLAlchemy connection string if successful, or None if an error occurs.
        """
        try:
            connection_string = await self.connect_to_database()
            return connection_string
        except Exception:
            return None
