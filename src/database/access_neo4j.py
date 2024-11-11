from neo4j import GraphDatabase
from .base import DatabaseConnector

class AccessNeo4j(DatabaseConnector):
    def __init__(self, uri: str, username: str, password: str):
        """
        Connect to the Neo4j database and generate the connection driver
        Args:
            uri (str): The URI for database authentication
            username (str): The username for database authentication
            password (str): The password  for password 
        """
        self.uri = uri
        self.username = username
        self.password = password
    
    async def connect_to_database(self) -> str:
        driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password), 
                                    connection_timeout=3000,
                                    max_connection_lifetime=300000)
        return driver
    
    async def main(self) -> str:
        try:
            driver = await self.connect_to_database()
            return driver
        except Exception:
            return None 
