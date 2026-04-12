import requests

BASE_URL = "http://127.0.0.1:8000"
API_URL  = f"{BASE_URL}/api/activities/"

def fetch_activities(timeout: int = 10):
    """Fetch grouped activities from the Django backend."""
    response = requests.get(API_URL, timeout=timeout)
    response.raise_for_status()
    return response.json()