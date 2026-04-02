# api/booking_api.py

import flet as ft

BOOKINGS = [
    {"id": "BK-001", "activity": "Catamaran Sunset Cruise", "icon": ft.Icons.SAILING, "date": "Thu, 10 Apr 2026", "time": "05:30 PM", "tickets": 2, "price": 4500, "status": "CONFIRMED"},
    {"id": "BK-004", "activity": "Snorkeling at Blue Bay", "icon": ft.Icons.WAVES, "date": "Sat, 25 Apr 2026", "time": "11:00 AM", "tickets": 4, "price": 2800, "status": "CONFIRMED"},
    {"id": "BK-002", "activity": "Scuba Diving – Beginner", "icon": ft.Icons.POOL, "date": "Fri, 20 Mar 2026", "time": "10:30 AM", "tickets": 1, "price": 6000, "status": "COMPLETED"},
    {"id": "BK-005", "activity": "Deep-Sea Fishing Trip", "icon": ft.Icons.ANCHOR, "date": "Sun, 08 Mar 2026", "time": "06:00 AM", "tickets": 3, "price": 7500, "status": "COMPLETED"},
    {"id": "BK-003", "activity": "Dolphin Watching", "icon": ft.Icons.WATER, "date": "Sun, 15 Feb 2026", "time": "07:00 AM", "tickets": 3, "price": 3000, "status": "CANCELLED"},
    {"id": "BK-006", "activity": "Glass-Bottom Boat Tour", "icon": ft.Icons.DIRECTIONS_BOAT, "date": "Tue, 03 Feb 2026", "time": "02:00 PM", "tickets": 2, "price": 1800, "status": "CANCELLED"},
]

def get_bookings():
    return BOOKINGS