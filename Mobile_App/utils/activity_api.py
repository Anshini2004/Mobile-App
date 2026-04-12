import requests

BASE_URL = "http://127.0.0.1:8000/grandblue"
API_URL = f"{BASE_URL}/api/activities/"
CACHE_KEY = "catalogue_data"


def fetch_activities(timeout: int = 10):
    response = requests.get(API_URL, timeout=timeout)
    response.raise_for_status()
    return response.json()


def preload_activities(page, timeout: int = 10):
    cached = page.session.store.get(CACHE_KEY)
    if cached:
        return cached

    data = fetch_activities(timeout=timeout)
    page.session.store.set(CACHE_KEY, data)
    return data