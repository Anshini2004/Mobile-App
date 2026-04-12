"""
Drop this file into mobile_app/views/catalogue_view.py (mobile-app project).
It replaces the existing catalogue_view.py entirely.

Requirements:
    pip install requests flet

The API is called at:
    GET http://127.0.0.1:8000/api/activities/

Change API_BASE_URL below if your Django server runs on a different host/port.

Tested against Flet 0.84.
"""

import threading

import flet as ft
import requests

# ─── Config ───────────────────────────────────────────────────────────────────

API_BASE_URL  = "http://127.0.0.1:8000"
CATALOGUE_URL = f"{API_BASE_URL}/api/activities/"

# Colour palette (mirrors the teal/white design in the mock-up)
TEAL_MAIN  = "#26B5A0"
TEAL_LIGHT = "#E0F5F2"
TEAL_DARK  = "#1A8C7A"
TEXT_DARK  = "#1A1A2E"
TEXT_MUTED = "#8E9BB0"
AMBER      = "#FFC107"
WHITE      = "#FFFFFF"
BLACK_78   = ft.Colors.with_opacity(0.25, "#000000")
BLACK_35   = ft.Colors.with_opacity(0.35, "#000000")
BLACK_12   = ft.Colors.with_opacity(0.12, "#000000")
SHADOW_TEAL = ft.Colors.with_opacity(0.18, TEAL_DARK)

CARD_WIDTH  = 188          # ~25% wider than original 150
CARD_HEIGHT = 110

# ─── Individual activity card ─────────────────────────────────────────────────

def build_activity_card(activity: dict) -> ft.Column:
    name        = activity.get("name", "—")
    description = activity.get("description", "No description available.")
    images      = activity.get("images", [])
    avg_rating  = activity.get("average_rating")
    image_url   = images[0] if images else None

    short_desc = description[:100] + "…" if len(description) > 100 else description

    # ── Overlay (opacity=0 by default, fades to 1 on hover) ──────────────────
    # Using opacity 0→1 instead of visible toggle so the animation actually runs
    overlay = ft.Container(
        content=ft.Text(
            short_desc,
            color=WHITE,
            size=10,
            text_align=ft.TextAlign.CENTER,
        ),
        bgcolor=BLACK_78,
        padding=ft.padding.all(8),
        alignment=ft.Alignment(0, 0),
        border_radius=ft.border_radius.all(12),
        width=CARD_WIDTH,
        height=CARD_HEIGHT,
        opacity=0,
        animate_opacity=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
    )

    # ── Background image (or teal fallback) ───────────────────────────────────
    if image_url:
        bg_image = ft.Image(
            src=image_url,
            fit="cover",
            width=CARD_WIDTH,
            height=CARD_HEIGHT,
            error_content=ft.Container(
                bgcolor=TEAL_LIGHT,
                width=CARD_WIDTH,
                height=CARD_HEIGHT,
                content=ft.Icon(ft.Icons.WAVES, color=TEAL_MAIN, size=32),
                alignment=ft.Alignment(0, 0),
            ),
        )
    else:
        bg_image = ft.Container(
            bgcolor=TEAL_LIGHT,
            width=CARD_WIDTH,
            height=CARD_HEIGHT,
            content=ft.Icon(ft.Icons.WAVES, color=TEAL_MAIN, size=32),
            alignment=ft.Alignment(0, 0),
        )

    card_stack = ft.Stack(
        controls=[bg_image, overlay],
        width=CARD_WIDTH,
        height=CARD_HEIGHT,
    )

    card_container = ft.Container(
        content=card_stack,
        width=CARD_WIDTH,
        height=CARD_HEIGHT,
        border_radius=ft.border_radius.all(12),
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=8,
            color=BLACK_12,
            offset=ft.Offset(0, 3),
        ),
        animate=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
    )

    # ── Hover handler via GestureDetector ─────────────────────────────────────
    # on_enter / on_exit are reliable even when an Image fills the card,
    # unlike Container.on_hover which can be swallowed by child widgets.
    def on_enter(e):
        overlay.opacity = 1
        overlay.update()

    def on_exit(e):
        overlay.opacity = 0
        overlay.update()

    card_gesture = ft.GestureDetector(
        content=card_container,
        on_enter=on_enter,
        on_exit=on_exit,
        on_tap=lambda _: None,          # placeholder — no navigation yet
    )

    # ── Activity name (tappable) ──────────────────────────────────────────────
    name_control = ft.GestureDetector(
        content=ft.Text(
            name,
            size=12,
            weight=ft.FontWeight.W_600,
            color=TEXT_DARK,
            width=CARD_WIDTH,
            overflow=ft.TextOverflow.ELLIPSIS,
            max_lines=1,
        ),
        on_tap=lambda _: None,
    )

    # ── Rating row ────────────────────────────────────────────────────────────
    if avg_rating is not None:
        rating_row = ft.Row(
            controls=[
                ft.Icon(ft.Icons.STAR, color=AMBER, size=13),
                ft.Text(
                    str(avg_rating),
                    size=12,
                    color=TEXT_DARK,
                    weight=ft.FontWeight.W_500,
                ),
            ],
            spacing=2,
            tight=True,
        )
    else:
        rating_row = ft.Text("No reviews", size=11, color=TEXT_MUTED, italic=True)

    return ft.Column(
        controls=[card_gesture, name_control, rating_row],
        spacing=4,
        tight=True,
    )


# ─── Category section ─────────────────────────────────────────────────────────

def build_category_section(category_data: dict):
    activity_type = category_data.get("activity_type", "")
    activities    = category_data.get("activities", [])

    if not activities:
        return None

    cards = [build_activity_card(a) for a in activities]

    scrollable_row = ft.Row(
        controls=cards,
        scroll=ft.ScrollMode.AUTO,
        spacing=18,
    )

    return ft.Column(
        controls=[
            ft.Text(
                activity_type,
                size=17,
                weight=ft.FontWeight.BOLD,
                color=TEXT_DARK,
            ),
            ft.Container(
                content=scrollable_row,
                padding=ft.padding.only(bottom=4),
            ),
        ],
        spacing=10,
    )


# ─── Grand Blue hero section ──────────────────────────────────────────────────
# Save the hero image as:  mobile_app/assets/hero_bg.png
# main.py must pass  assets_dir="assets"  to ft.app() — see bottom of this file.
HERO_IMAGE_SRC = "/hero_bg.jpg"

def build_hero_banner() -> ft.Container:
    """
    Full-width hero taking ~1/3 of vertical space (300px on a 900px window).
    Background: user-supplied ocean aerial photo with a dark teal overlay.
    Title and slogan are left-aligned. 'Explore' + arrow is near the bottom.
    """
    title = ft.Text(
        "Grand Blue",
        size=38,
        weight=ft.FontWeight.BOLD,
        color=WHITE,
        text_align=ft.TextAlign.LEFT,
    )

    slogan = ft.Text(
        "Above & Below Sea Level",
        size=15,
        weight=ft.FontWeight.W_400,
        color=ft.Colors.with_opacity(0.88, WHITE),
        text_align=ft.TextAlign.LEFT,
        italic=True,
    )

    explore = ft.Column(
        controls=[
            ft.Text(
                "Explore",
                size=13,
                color=ft.Colors.with_opacity(0.90, WHITE),
                weight=ft.FontWeight.W_600,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.Icon(ft.Icons.KEYBOARD_ARROW_DOWN_ROUNDED, color=WHITE, size=20),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=0,
        tight=True,
    )

    content = ft.Column(
        controls=[
            ft.Container(expand=True),    # push title block to vertical centre
            title,
            ft.Container(height=4),
            slogan,
            ft.Container(expand=3),       # tall spacer pushes explore well down
            ft.Row(
                controls=[explore],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Container(height=4),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.START,
        expand=True,
        spacing=0,
    )

    # Dark semi-transparent teal overlay so text stays readable over the photo
    overlay = ft.Container(
        expand=True,
        bgcolor=ft.Colors.with_opacity(0.0, "#0D3B33"),
    )

    return ft.Container(
        content=ft.Stack(
            controls=[overlay, ft.Container(content=content, expand=True)],
            expand=True,
        ),
        height=300,
        border_radius=ft.border_radius.all(18),
        image=ft.DecorationImage(
            src=HERO_IMAGE_SRC,
            fit="cover",
        ),
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=20,
            color=SHADOW_TEAL,
            offset=ft.Offset(0, 6),
        ),
        padding=ft.padding.symmetric(horizontal=24, vertical=20),
    )


# ─── Main catalogue view ──────────────────────────────────────────────────────

def catalogue_view(page: ft.Page) -> ft.Column:
    """Entry point. Returns a ft.Column ready to be added to the page."""

    loading_ring = ft.Container(
        content=ft.Column(
            controls=[
                ft.ProgressRing(width=36, height=36, stroke_width=3, color=TEAL_MAIN),
                ft.Text("Loading activities…", color=TEXT_MUTED, size=13),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
        ),
        alignment=ft.Alignment(0, 0),
        padding=ft.padding.only(top=60),
        visible=True,
    )

    error_text = ft.Text("", color="#E53935", size=13, expand=True)
    error_banner = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.ERROR_OUTLINE_ROUNDED, color="#E53935", size=18),
                error_text,
            ],
            spacing=8,
        ),
        bgcolor="#FFEBEE",
        border_radius=ft.border_radius.all(10),
        padding=ft.padding.symmetric(horizontal=14, vertical=10),
        visible=False,
    )

    # Activity sections populated after fetch (hero is always shown above)
    content_col = ft.Column(
        controls=[],
        spacing=20,
        visible=False,
    )

    def load_catalogue():
        try:
            response = requests.get(CATALOGUE_URL, timeout=10)
            response.raise_for_status()
            data = response.json()

            content_col.controls.clear()

            for category in data:
                section = build_category_section(category)
                if section is not None:
                    content_col.controls.append(section)

            loading_ring.visible = False
            content_col.visible  = True

        except requests.exceptions.ConnectionError:
            loading_ring.visible = False
            error_banner.visible = True
            error_text.value     = "Could not connect to the server. Is it running on port 8000?"

        except requests.exceptions.Timeout:
            loading_ring.visible = False
            error_banner.visible = True
            error_text.value     = "Request timed out. Please try again."

        except Exception as exc:
            loading_ring.visible = False
            error_banner.visible = True
            error_text.value     = f"Unexpected error: {exc}"

        page.update()

    threading.Thread(target=load_catalogue, daemon=True).start()

    # Wrap everything in a padded container so nothing touches the edges
    inner = ft.Column(
        controls=[
            build_hero_banner(),
            error_banner,
            loading_ring,
            content_col,
        ],
        spacing=20,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    return ft.Container(
        content=inner,
        padding=ft.padding.symmetric(horizontal=18, vertical=14),
        expand=True,
    )


# Alias expected by main.py
activities_page = catalogue_view