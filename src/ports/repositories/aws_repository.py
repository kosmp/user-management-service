from abc import ABC, abstractmethod


class AwsAbstractRepository(ABC):
    @abstractmethod
    async def add_one(self, body: bytes, key: str):
        pass

    @abstractmethod
    async def get(self, key: str):
        pass

    @abstractmethod
    async def delete(self, key: str):
        pass
