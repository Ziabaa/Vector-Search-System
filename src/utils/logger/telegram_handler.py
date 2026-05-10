import logging
import requests

from config import settings


class TelegramHandler(logging.Handler):

    def __init__(
            self,
            token: str = settings.telegram_logging.bot_token,
            chat_id: int = settings.telegram_logging.chat_id,
            level=logging.ERROR,
    ):
        super().__init__(level)

        self.token = token
        self.chat_id = chat_id

    def emit(self, record):

        try:
            message = self.format(record)

            url = (
                f"https://api.telegram.org"
                f"/bot{self.token}/sendMessage"
            )

            params = {
                "chat_id": self.chat_id,
                "text": message,
            }

            requests.get(
                url,
                params=params,
                timeout=5,
            )

        except Exception:
            self.handleError(record)
