# main.py

import sys
from pathlib import Path

# Add the current directory to sys.path to allow absolute imports
sys.path.append(str(Path(__file__).parent))

import flet as ft
from views.booking_view import bookings_page
from utils.constants import BG

def main(page: ft.Page):
    page.title = "My Bookings"
    page.bgcolor = BG
    page.window.width = 550
    page.window.height = 900

    page.add(bookings_page(page, user_id=8)
    )

ft.run(main)