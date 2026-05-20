import json
from functools import wraps

from src.ai.gpt_client import GptClient
from src.db.program.db import ProgramDb
from src.services.models import ProgramResponse, FoundedTool
from src.functions.base.tool import BaseTool
from src.functions.get_weather import GetWeather
from src.functions.google_search import GoogleSearch
from src.functions.get_uah_rates import GetUahRates
from vector.tools_repository import ToolRepository


class Program:
    def __init__(self):
        self.available_tools = {
            "GetWeather": GetWeather,
            "GoogleSearch": GoogleSearch,
            "GetUahRates": GetUahRates,
        }
        self.ai_client = GptClient()
        self.db = ProgramDb()

    @staticmethod
    def _save_to_db(func):
        @wraps(func)
        def wrapper(self, query: str, *args, **kwargs) -> ProgramResponse:
            request_id = self.db.create_request(message=query)

            response: ProgramResponse = func(self, query, *args, **kwargs)

            functions = [
                {
                    "name": tool.name,
                    "params": json.dumps(tool.params, ensure_ascii=False),
                }
                for tool in (response.founded_functions or [])
            ]

            self.db.create_response(
                request_id=request_id,
                message=response.answer or "",
                functions=functions,
            )

            return response

        return wrapper

    @_save_to_db
    def get_answer(self, query: str) -> ProgramResponse:
        response = ProgramResponse()
        tools = self.get_functions(query)

        if not tools:
            response.answer = "Я не нашёл подходящих инструментов для запроса."
            return response

        final_answers = []

        for tool in tools:
            if not tool.can_execute:
                params = [
                    p.get_for_ai_request()
                    for p in tool.params
                    if p.value is None
                ]

                if params:
                    result = self.ai_client.ask_llm_for_params(
                        user_message=query,
                        function_name=tool.name,
                        params="\n".join(params),
                    )

                    for param in tool.params:
                        if param.name in result["params"]:
                            param.value = result["params"][param.name]

            tool_result = tool.execute()

            response.founded_functions.append(
                FoundedTool(
                    name=tool.name,
                    params={p.name: p.value for p in tool.params},
                ),
            )

            answer = self.ai_client.ask_llm_for_final_answer(
                user_query=query,
                function_name=tool.name,
                function_result=tool_result,
            )

            final_answers.append(answer)

        response.answer = "\n\n".join(final_answers)
        for tool in tools:
            tool.clear_params()
        return response

    def get_functions(self, query: str, limit: int = 2) -> list[BaseTool]:
        result = ToolRepository().search(query=query, limit=limit)

        tools: list[BaseTool] = []

        for item in result:
            tool_class = self.available_tools.get(item.tool_name)

            if not tool_class:
                continue

            tools.append(tool_class())

        return tools


if __name__ == '__main__':
    res = Program().get_answer("погода в киеве")
    print(res)
