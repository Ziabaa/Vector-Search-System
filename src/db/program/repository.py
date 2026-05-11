from abc import ABC, abstractmethod


class IProgramRepository(ABC):

    @abstractmethod
    def create_request(self, message: str) -> int:
        pass

    @abstractmethod
    def create_response(
            self,
            request_id: int,
            message: str,
            functions: list[dict],
    ) -> int:
        pass
