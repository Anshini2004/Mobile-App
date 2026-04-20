# views/components.py

import flet as ft
from utils.constants import *

def chip(icon, text: str):
    return ft.Row(spacing=4, controls=[ft.Icon(icon, size=13, color=TEXT_MUTED), ft.Text(text, size=11, color=TEXT_MUTED)])

def stat_tile(value: str, label: str, color: str):
    return ft.Container(
        expand=True,
        padding=pad_sym(h=6, v=12),
        bgcolor=CARD_BG,
        border_radius=14,
        border=ft.Border.all(1, BORDER),
        content=ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=3, tight=True, controls=[
            ft.Text(value, size=19, weight=ft.FontWeight.W_800, color=color),
            ft.Text(label, size=10, color=TEXT_MUTED, text_align=ft.TextAlign.CENTER),
        ])
    )

def nav_btn(icon, label: str, active: bool = False):
    return ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=3, tight=True, controls=[
        ft.Icon(icon, size=21, color=TEAL if active else TEXT_MUTED),
        ft.Text(label, size=9, color=TEAL if active else TEXT_MUTED, weight=ft.FontWeight.W_600 if active else ft.FontWeight.W_400),
    ])