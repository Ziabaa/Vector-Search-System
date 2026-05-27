import json
from openai import OpenAI

from config import settings


class GptClient:

    def __init__(self):
        self.client = OpenAI(api_key=settings.ai_providers.openai_key)


    def ask_llm_for_params(self, function_name: str, params: str, user_message: str) -> dict:
        prompt = f"""
        You are a function parameter filler.
        
        User message: {user_message}
        
        Function: {function_name}
        
        Fill missing parameters with best possible values.
        
        Return ONLY valid JSON in format:
        {{
          "params": {{
            "param_name": "value"
          }}
        }}
        
        Parameters to fill:
        {params}
        """

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Return only valid JSON. No explanation."},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
        )

        return json.loads(response.choices[0].message.content)

    def ask_llm_for_final_answer(
            self,
            user_query: str,
            functions_results: str,
    ) -> str:
        prompt = f"""
        You are an assistant that explains results of function execution.

        User request:
        {user_query}

        Function execution results:
        {functions_results}

        Rules:
        - Always respond in Ukrainian
        - Keep the answer short and concise (1–3 sentences)
        - Do not mention JSON
        - Do not mention internal functions or tools
        - Use only the provided result
        - If result is empty, say that nothing was found

        Return only the final answer.
        """

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You convert tool results into natural language answers.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.3,
        )

        return response.choices[0].message.content
