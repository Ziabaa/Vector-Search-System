from src.db.base_db import BaseDb
from src.db.program.repository import IProgramRepository


class ProgramDb(BaseDb, IProgramRepository):

    def create_request(self, message: str) -> int:
        query = """
                INSERT INTO Requests (Message)
                    OUTPUT INSERTED.Id
                VALUES (%s)
                """

        result = self.fetch_one(query, (message,))
        return result["Id"]

    def create_response(
            self,
            request_id: int,
            message: str,
            functions: list[dict],
    ) -> int:
        query = """
                INSERT INTO Responses (RequestId, Message)
                    OUTPUT INSERTED.Id
                VALUES (%s, %s)
                """

        result = self.fetch_one(query, (request_id, message))
        response_id = result["Id"]

        self._insert_function_executions(response_id, functions)

        return response_id

    def _insert_function_executions(
            self,
            response_id: int,
            functions: list[dict],
    ) -> None:
        if not functions:
            return

        query = """
                INSERT INTO FunctionExecutions (ResponseId, Name, Params)
                VALUES (%s, %s, %s)
                """

        params = [
            (response_id, fn["name"], fn.get("params"))
            for fn in functions
        ]

        self.execute_many(query, params)
