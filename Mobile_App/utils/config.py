USE_PHONE = False # Set to True when testing on a physical phone, False for local development on PC

LOCAL_HOST = "http://127.0.0.1:8000"
PHONE_HOST = ""  # change only here when needed

HOST = PHONE_HOST if USE_PHONE else LOCAL_HOST

API_BASE_URL = f"{HOST}/grandblue"
IMAGE_BASE_URL = HOST