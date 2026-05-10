import requests
from config import settings


def google_search(query: str, limit: int = 5) -> list[dict]:
    url = "https://serpapi.com/search.json"

    params = {
        "q": query,
        "engine": "google",
        "api_key": settings.authorisation.SERPAPI_KEY,
    }

    r = requests.get(url, params=params)
    data = r.json()

    results = []

    for item in data.get("organic_results", [])[:limit]:
        results.append(
            {
                "title": item.get("title"),
                "link": item.get("link"),
                "snippet": item.get("snippet"),
            },
        )

    return results


if __name__ == '__main__':
    query = "Семантичний пошук"
    res = google_search(query)
    print(res)