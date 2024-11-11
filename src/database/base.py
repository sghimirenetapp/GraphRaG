from abc import ABC, abstractmethod
from typing import Optional


class DatabaseConnector(ABC):
    @abstractmethod
    async def connect_to_database(self) -> str:
        pass

    @abstractmethod
    async def main(self) -> Optional[str]:
        pass
