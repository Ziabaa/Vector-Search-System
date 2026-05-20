from abc import ABC, abstractmethod

from src.functions.base.param import Param


class BaseTool(ABC):
    """
    Base abstract tool.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def params(self) -> list[Param]:
        pass

    @abstractmethod
    def execute(self, **kwargs) -> str:
        pass

    def execute_tool(self, **kwargs) -> str:
        if self.can_execute:
            return self.execute(**kwargs)
        raise AttributeError("Some params are not set")

    @property
    def can_execute(self) -> bool:
        for param in self.params:
            if param.value is None:
                return False
        return True

    def clear_params(self):
        for param in self.params:
            param.value = None
