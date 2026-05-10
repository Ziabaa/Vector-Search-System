import requests


def get_uah_rates() -> list[dict]:
    url = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json"
    r = requests.get(url)
    return r.json()


if __name__ == '__main__':
    res = get_uah_rates()
    print(res)
