from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Type
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseRepository(ABC, Generic[T]):
    def __init__(self, model: Type[T], collection_name: str) -> None:
        self.model = model
        self.collection_name = collection_name

    @abstractmethod
    def search(self, query: str, limit: int = 5, **kwargs) -> list[T]:
        ...

    @abstractmethod
    def insert(self, obj: T) -> None:
        ...

    @abstractmethod
    def insert_many(self, objects: list[T]) -> None:
        ...

    @abstractmethod
    def update(self, uuid: str, obj: T) -> None:
        ...

    @abstractmethod
    def delete(self, uuid: str) -> None:
        ...

    @staticmethod
    def _to_dict(obj: T) -> dict:
        """Сериалізація моделі → dict (без None-значень)."""
        return obj.model_dump(exclude_none=True)

    def _from_dict(self, data: dict) -> T:
        """Десериалізація dict → модель."""
        return self.model.model_validate(data)
