# utils/constants.py

import flet as ft

TEAL        = "#3BBFB2"
TEAL_LIGHT  = "#E8F8F7"
BG          = "#F4F7F7"
CARD_BG     = "#FFFFFF"
TEXT_DARK   = "#1A2E2D"
TEXT_MUTED  = "#7B9492"
BORDER      = "#DDE8E7"

STATUS_CFG = {
    "CONFIRMED": {"bg": "#E6F9F0", "fg": "#1A9B5F", "label": "Confirmed"},
    "COMPLETED": {"bg": "#E8F0FE", "fg": "#1A5FBB", "label": "Completed"},
    "CANCELLED": {"bg": "#FDE8E8", "fg": "#C0392B", "label": "Cancelled"},
}

CENTER = ft.Alignment(0, 0)

def pad_all(v): return ft.Padding(v, v, v, v)
def pad_sym(h=0, v=0): return ft.Padding(h, v, h, v)
def pad_only(left=0, right=0, top=0, bottom=0):
    return ft.Padding(left, top, right, bottom)