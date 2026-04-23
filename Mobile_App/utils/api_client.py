import requests

BASE_URL = "http://127.0.0.1:8000/grandblue"
API_BASE_URL = f"{BASE_URL}/api"


def _json_or_default(response):
    try:
        return response.json()
    except Exception:
        return {}


def get_auth_headers(page):
    access = page.session.store.get("access_token")
    if not access:
        return {}
    return {
        "Authorization": f"Bearer {access}"
    }


def save_auth_session(page, payload):
    user = payload.get("user", {})
    tokens = payload.get("tokens", {})

    page.session.store.set("access_token", tokens.get("access", ""))
    page.session.store.set("refresh_token", tokens.get("refresh", ""))

    page.session.store.set("user_id", user.get("id"))
    page.session.store.set(
        "user_name",
        user.get("full_name") or user.get("username") or user.get("email")
    )
    page.session.store.set(
        "user_username",
        user.get("username") or user.get("email")
    )
    page.session.store.set("user_email", user.get("email", ""))
    page.session.store.set("user_data", user)


def clear_auth_session(page):
    keys = [
        "access_token",
        "refresh_token",
        "user_id",
        "user_name",
        "user_username",
        "user_email",
        "user_data",
    ]
    for key in keys:
        if page.session.store.contains_key(key):
            page.session.store.remove(key)


def api_register(data):
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/register/",
            json=data,
            timeout=20,
        )
        payload = _json_or_default(response)
        return {
            "ok": response.status_code == 201,
            "status_code": response.status_code,
            "data": payload,
        }
    except requests.ConnectionError:
        return {
            "ok": False,
            "fatal": "Cannot connect to Django API server.",
        }
    except Exception as exc:
        return {
            "ok": False,
            "fatal": str(exc),
        }


def api_login(data):
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/login/",
            json=data,
            timeout=20,
        )
        payload = _json_or_default(response)
        return {
            "ok": response.status_code == 200,
            "status_code": response.status_code,
            "data": payload,
        }
    except requests.ConnectionError:
        return {
            "ok": False,
            "fatal": "Cannot connect to Django API server.",
        }
    except Exception as exc:
        return {
            "ok": False,
            "fatal": str(exc),
        }


def api_get_me(page):
    try:
        response = requests.get(
            f"{API_BASE_URL}/auth/me/",
            headers=get_auth_headers(page),
            timeout=20,
        )
        payload = _json_or_default(response)
        return {
            "ok": response.status_code == 200,
            "status_code": response.status_code,
            "data": payload,
        }
    except requests.ConnectionError:
        return {
            "ok": False,
            "fatal": "Cannot connect to Django API server.",
        }
    except Exception as exc:
        return {
            "ok": False,
            "fatal": str(exc),
        }

def api_update_me(page, data):
    try:
        response = requests.patch(
            f"{API_BASE_URL}/auth/me/",
            json=data,
            headers=get_auth_headers(page),
            timeout=20,
        )
        payload = _json_or_default(response)
        return {
            "ok": response.status_code == 200,
            "status_code": response.status_code,
            "data": payload,
        }
    except Exception as exc:
        return {
            "ok": False,
            "fatal": str(exc),
        }

def api_refresh_token(page):
    refresh_token = page.session.store.get("refresh_token")
    if not refresh_token:
        return {"ok": False, "fatal": "No refresh token found."}

    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/token/refresh/",
            json={"refresh": refresh_token},
            timeout=20,
        )
        payload = _json_or_default(response)

        if response.status_code == 200:
            new_access = payload.get("access")
            new_refresh = payload.get("refresh")

            if new_access:
                page.session.store.set("access_token", new_access)
            if new_refresh:
                page.session.store.set("refresh_token", new_refresh)

            return {"ok": True, "data": payload}

        return {
            "ok": False,
            "status_code": response.status_code,
            "data": payload,
        }
    except Exception as exc:
        return {"ok": False, "fatal": str(exc)}


def api_logout(page):
    refresh_token = page.session.store.get("refresh_token")
    if not refresh_token:
        clear_auth_session(page)
        return {"ok": True}

    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/logout/",
            json={"refresh": refresh_token},
            headers=get_auth_headers(page),
            timeout=20,
        )
        clear_auth_session(page)
        return {"ok": response.status_code in [200, 205]}
    except Exception:
        clear_auth_session(page)
        return {"ok": True}