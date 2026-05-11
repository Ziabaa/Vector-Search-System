from abc import ABC, abstractmethod
from typing import Any, Optional


class Param(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @property
    @abstractmethod
    def value(self) -> Any:
        pass

    @value.setter
    def value(self, value):
        self._value = value

    def get_for_ai_request(self) -> str:
        return self.name + ": " + self.description


class CityParam(Param):
    """
    City parameter.
    """

    @property
    def name(self) -> str:
        return "city"

    @property
    def description(self) -> str:
        return "City name"

    value: Optional[str] = None


class QueryParam(Param):
    """
    City parameter.
    """

    @property
    def name(self) -> str:
        return "query"

    @property
    def description(self) -> str:
        return "Search query for Google"

    value: Optional[str] = None


class LimitParam(Param):
    """
    City parameter.
    """

    @property
    def name(self) -> str:
        return "limit"

    @property
    def description(self) -> str:
        return "Number of search results"

    value: int = 3
