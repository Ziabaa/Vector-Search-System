from abc import ABC, abstractmethod


class IDialogRepository(ABC):

    @abstractmethod
    def create_dialog(self, name: str) -> int:
        pass

    @abstractmethod
    def create_request(
            self,
            dialog_id: int,
            message: str,
    ) -> int:
        pass

    @abstractmethod
    def create_response(
            self,
            request_id: int,
            message: str,
    ) -> int:
        pass

    @abstractmethod
    def set_request_response(
            self,
            request_id: int,
            response_message: str,
    ) -> None:
        pass
