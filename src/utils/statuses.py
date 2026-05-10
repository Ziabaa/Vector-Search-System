from typing import Union

from pydantic import BaseModel


class Status(BaseModel):
    status: int
    message: str = ""

    def __eq__(self, other: object) -> Union[AttributeError | bool]:
        if not isinstance(other, Status):
            return AttributeError("Cannot compare Status with a non-Status object")
        return self.status == other.status


class Statuses:

    @staticmethod
    def success(message: str = "") -> Status:
        return Status(
            status=1,
            message=message,
        )

    @staticmethod
    def error(message: str = "") -> Status:
        return Status(
            status=2,
            message=message,
        )

    @staticmethod
    def not_found(message: str = "") -> Status:
        return Status(
            status=3,
            message=message,
        )
