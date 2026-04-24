# api/booking_api.py

import httpx
import flet as ft

BASE_URL = "http://127.0.0.1:8000/grandblue/api"

ICON_MAP = {
    "catamaran": ft.Icons.SAILING,
    "cruise": ft.Icons.SAILING,
    "snorkel": ft.Icons.WAVES,
    "scuba": ft.Icons.POOL,
    "diving": ft.Icons.POOL,
    "fishing": ft.Icons.ANCHOR,
    "dolphin": ft.Icons.WATER,
    "glass": ft.Icons.DIRECTIONS_BOAT,
    "boat": ft.Icons.DIRECTIONS_BOAT,
    "kayak": ft.Icons.ROWING,
    "surf": ft.Icons.SURFING,
}

def resolve_icon(activity_name: str):
    name_lower = activity_name.lower()
    for keyword, icon in ICON_MAP.items():
        if keyword in name_lower:
            return icon
    return ft.Icons.EXPLORE


def format_booking(b: dict) -> dict:
    from datetime import datetime
    raw_date = b.get("date", "")
    try:
        dt = datetime.strptime(raw_date, "%Y-%m-%d")
        formatted_date = dt.strftime("%a, %d %b %Y")
    except Exception:
        formatted_date = raw_date

    return {
        "id":       f"BK-{str(b['id']).zfill(3)}",
        "db_id":    b["id"],          # keep raw int for API calls
        "activity": b.get("activity_name", "Unknown Activity"),
        "icon":     resolve_icon(b.get("activity_name", "")),
        "date":     formatted_date,
        "time":     "TBD",
        "tickets":  b.get("group_size", 1),
        "price":    float(b.get("price_total", 0)),
        "status":   b.get("status", "CONFIRMED"),
    }


async def get_bookings(user_id: int) -> list[dict]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/bookings/{user_id}/", timeout=10)
        response.raise_for_status()
        raw = response.json()
        return [format_booking(b) for b in raw]


async def cancel_booking(db_id: int) -> bool:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{BASE_URL}/bookings/{db_id}/cancel/",
                timeout=10
            )
            return response.status_code == 200
    except Exception as e:
        print(f"[booking_api] Error cancelling booking: {e}")
        return False