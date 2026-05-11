import requests

from src.functions.base.tool import BaseTool


class GetUahRates(BaseTool):
    """
    Get UAH exchange rates from NBU.
    """
    name = "GetUahRates"
    params = []

    def execute(self) -> str:
        url = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json"

        response = requests.get(url)
        response.raise_for_status()

        rates = response.json()

        needed = {
            "USD": "Долар США",
            "EUR": "Євро",
            "GBP": "Фунт стерлінгів",
            "XAU": "Золото",
            "XAG": "Срібло",
            "XPT": "Платина",
        }

        lines = ["Курси валют та металів НБУ\n"]

        for item in rates:
            if item["cc"] in needed:
                lines.append(
                    f"{needed[item['cc']]:<20} "
                    f"{item['rate']:>12,.4f} грн"
                )

        lines.append(f"\nДата оновлення: {rates[0]['exchangedate']}")

        return "\n".join(lines)


if __name__ == '__main__':
    print(UahRatesTool().execute())