from src.db.base_db import BaseDb
from src.db.dialog.repository import IDialogRepository


class DialogDb(BaseDb, IDialogRepository):

    def create_dialog(self, name: str) -> int:
        query = """
                INSERT INTO Dialogs (Name)
                    OUTPUT INSERTED.Id
                VALUES (%s) \
                """

        result = self.fetch_one(query, (name,))
        return result["Id"]

    def create_request(
            self,
            dialog_id: int,
            message: str,
    ) -> int:
        query = """
                INSERT INTO Requests (DialogId, Message)
                    OUTPUT INSERTED.Id
                VALUES (%s, %s) \
                """

        result = self.fetch_one(
            query,
            (dialog_id, message),
        )

        return result["Id"]

    def create_response(
            self,
            request_id: int,
            message: str,
    ) -> int:
        query = """
                INSERT INTO Responses (RequestId, Message)
                    OUTPUT INSERTED.Id
                VALUES (%s, %s) \
                """

        result = self.fetch_one(
            query,
            (request_id, message),
        )

        return result["Id"]

    def set_request_response(
            self,
            request_id: int,
            response: str,
    ) -> None:
        query = """
                UPDATE Requests
                SET Response = %s
                WHERE Id = %s \
                """

        self.execute(
            query,
            (response, request_id),
        )
