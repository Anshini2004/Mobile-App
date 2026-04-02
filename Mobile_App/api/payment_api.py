import requests

BASE_URL = "http://127.0.0.1:8000/api"


def process_payment(data):
    try:
        response = requests.post(f"{BASE_URL}/payment/", json=data)
        return response.status_code, response.json()
    except Exception as e:
        return 500, {"error": str(e)}