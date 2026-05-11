import pymssql
from typing import Optional

from config import settings


class BaseDb:

    def __init__(
            self,
            server: str = settings.database.server,
            user: str = settings.database.user,
            password: str = settings.database.password,
            database: str = settings.database.database,
    ):
        self.server = server
        self.user = user
        self.password = password
        self.database = database

    def _get_connection(self):
        return pymssql.connect(
            server=self.server,
            user=self.user,
            password=self.password,
            database=self.database,
            as_dict=True,
        )

    def execute(
            self,
            query: str,
            params: Optional[tuple] = None,
    ) -> None:
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params or ())
                connection.commit()

    def fetch_one(
            self,
            query: str,
            params: Optional[tuple] = None,
    ) -> Optional[dict]:
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params or ())
                result = cursor.fetchone()
                connection.commit()
                return result

    def execute_many(
            self,
            query: str,
            params: list[tuple],
    ) -> None:
        if not params:
            return

        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.executemany(query, params)
                connection.commit()
