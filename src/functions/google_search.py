# src/functions/tools/google_search_tool.py

import requests
from bs4 import BeautifulSoup

from config import settings
from src.functions.base.tool import BaseTool
from src.functions.base.param import Param, QueryParam, LimitParam
from utils.logger.logger import logger


class GoogleSearch(BaseTool):
    """
    Google search tool using SerpAPI + page extraction.
    """

    name = "GoogleSearch"
    params: list[Param] = [QueryParam(), LimitParam()]

    def _get_param(self, name: str):
        return next(p.value for p in self.params if p.name == name)

    @staticmethod
    def get_page_text(url: str, limit: int = 1000) -> str:
        try:
            response = requests.get(
                url,
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=10,
            )

            soup = BeautifulSoup(response.text, "html.parser")

            paragraphs = soup.find_all("p")

            text = " ".join(
                (p.get_text(" ", strip=True) for p in paragraphs)
            )

            text = " ".join(text.split())

            return text[:limit] + "..."

        except Exception as e:
            logger.error(f"Error fetching page text: {e}")
            return "Не вдалося отримати текст"

    def execute(self) -> str:
        query = self._get_param("query")
        limit = self._get_param("limit")

        url = "https://serpapi.com/search.json"

        params = {
            "q": query,
            "engine": "google",
            "api_key": settings.authorisation.SERPAPI_KEY,
        }

        response = requests.get(url, params=params)
        data = response.json()

        results = []

        for item in data.get("organic_results", [])[:limit]:
            link = item.get("link")

            results.append(
                {
                    "title": item.get("title"),
                    "link": link,
                    "snippet": self.get_page_text(link),
                },
            )

        lines = []

        for index, item in enumerate(results, start=1):
            lines.append(f"Результат #{index}")
            lines.append(f"Заголовок: {item['title']}")
            lines.append(f"Посилання: {item['link']}")
            lines.append(f"Текст:\n{item['snippet']}")
            lines.append(f"При формуванні відповіді обов'язково надати одне посилання на інформацію.")
            lines.append("")

        return "\n".join(lines)


if __name__ == '__main__':
    tool = GoogleSearch()
    for tool_param in tool.params:
        if tool_param.name == 'query':
            tool_param.value = 'cемантичний пошук'
    print(tool.execute_tool())
