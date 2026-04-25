import asyncio

import flet as ft
import requests
from utils.config import API_BASE_URL, IMAGE_BASE_URL

# ─── Config ───────────────────────────────────────────────────────────────────
CATALOGUE_URL = f"{API_BASE_URL}/api/activities-catalogue/"

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

CARD_WIDTH  = 188
CARD_HEIGHT = 110

CACHE_KEY = "catalogue_data"

def fix_image_url(url):
    if not url:
        return None

    url = str(url)

    if url.startswith("http://127.0.0.1:8000"):
        return url.replace("http://127.0.0.1:8000", IMAGE_BASE_URL)

    if url.startswith("http://localhost:8000"):
        return url.replace("http://localhost:8000", IMAGE_BASE_URL)

    if url.startswith("http://") or url.startswith("https://"):
        return url

    if url.startswith("/"):
        return f"{IMAGE_BASE_URL}{url}"

    return f"{IMAGE_BASE_URL}/{url}"


def build_activity_card(page: ft.Page, activity: dict) -> ft.Column:
    name = activity.get("name", "—")
    description = activity.get("description", "No description available.")
    avg_rating = activity.get("avg_rating") or activity.get("average_rating")

    images = activity.get("images", [])

    image_url = None

    if isinstance(images, list) and len(images) > 0:
        first_image = images[0]

        if isinstance(first_image, dict):
            image_url = first_image.get("image_url") or first_image.get("image")
        else:
            image_url = first_image

    if not image_url:
        image_url = activity.get("image") or activity.get("image_url")

    image_url = fix_image_url(image_url)


    short_desc = description[:100] + "…" if len(description) > 100 else description

    overlay = ft.Container(
        content=ft.Text(short_desc, color=WHITE, size=10, text_align=ft.TextAlign.CENTER),
        bgcolor=BLACK_78,
        padding=8,
        alignment=ft.Alignment(0, 0),
        border_radius=12,
        width=CARD_WIDTH,
        height=CARD_HEIGHT,
        opacity=0,
        animate_opacity=200,
    )

    if image_url:
        bg_image = ft.Image(
            src=image_url,
            fit="cover",
            width=CARD_WIDTH,
            height=CARD_HEIGHT,
        )
    else:
        bg_image = ft.Container(
            bgcolor=TEAL_LIGHT,
            width=CARD_WIDTH,
            height=CARD_HEIGHT,
            content=ft.Icon(ft.Icons.WAVES, color=TEAL_MAIN),
            alignment=ft.Alignment(0, 0),
        )

    stack = ft.Stack([bg_image, overlay], width=CARD_WIDTH, height=CARD_HEIGHT)

    def on_enter(e):
        overlay.opacity = 1
        overlay.update()

    def on_exit(e):
        overlay.opacity = 0
        overlay.update()

    def go_to_activity(e):
        page.go(f"/activity/{activity['id']}")

    card = ft.GestureDetector(
        content=ft.Container(
            content=stack,
            border_radius=12,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
        ),
        on_enter=on_enter,
        on_exit=on_exit,
        on_tap=go_to_activity,
    )

    if avg_rating is not None:
        rating = ft.Row(
            [
                ft.Icon(ft.Icons.STAR, color=AMBER, size=13),
                ft.Text(str(avg_rating)),
            ]
        )
    else:
        rating = ft.Text("No reviews", size=11, color=TEXT_MUTED)

    return ft.Column(
        [card, ft.Text(name), rating],
        spacing=4,
    )


def build_category_section(page: ft.Page, category_data: dict):
    activity_type = category_data.get("activity_type", "")
    activities = category_data.get("activities", [])

    if not activities:
        return None

    cards = [build_activity_card(page, a) for a in activities]

    return ft.Column(
        controls=[
            ft.Text(activity_type, size=17, weight=ft.FontWeight.BOLD),
            ft.Row(
                controls=cards,
                scroll=ft.ScrollMode.AUTO,
                spacing=12,
            )
        ]
    )


HERO_IMAGE_SRC = "/hero_bg.jpg"

def build_hero_banner() -> ft.Container:
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
            ft.Container(expand=True),
            title,
            ft.Container(height=4),
            slogan,
            ft.Container(expand=3),
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


def catalogue_view(page: ft.Page) -> ft.Column:
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

    content_col = ft.Column(
        controls=[],
        spacing=20,
        visible=False,
    )

    def normalize_catalogue_data(data):
        if not data:
            return []

        # Already flat: [{id, name, image, ...}]
        if isinstance(data, list) and data and "id" in data[0]:
            return data

        # Grouped: [{activity_type, activities: [...]}]
        if isinstance(data, list) and data and "activities" in data[0]:
            flat = []
            for group in data:
                for activity in group.get("activities", []):
                    activity.setdefault("activity_type", group.get("activity_type", "Other"))
                    flat.append(activity)
            return flat

        return []

    def populate_sections(data):
        data = normalize_catalogue_data(data)

        content_col.controls.clear()

        grouped = {}

        for activity in data:
            atype = activity.get("activity_type", "Other")
            if atype not in grouped:
                grouped[atype] = []
            grouped[atype].append(activity)

        for activity_type, activities in grouped.items():

            section = ft.Column(
                controls=[
                    ft.Text(activity_type, size=17, weight=ft.FontWeight.BOLD),

                    ft.Container(                          # FIX 2: Row + ALWAYS scrollbar
                        content=ft.Row(
                            controls=[
                                build_activity_card(page, a) for a in activities
                            ],
                            scroll=ft.ScrollMode.ALWAYS,
                            spacing=12,
                        ),
                        height=200,                        # +20 to give scrollbar breathing room
                    ),
                ]
            )

            content_col.controls.append(section)

        loading_ring.visible = False
        content_col.visible = True
        page.update()

    async def load_catalogue():
        try:
            cached_data = page.session.store.get(CACHE_KEY)
            if cached_data:
                populate_sections(cached_data)
                return

            response = await asyncio.to_thread(requests.get,CATALOGUE_URL, timeout=10)
            response.raise_for_status()
            data = response.json()

            page.session.store.set(CACHE_KEY, data)
            populate_sections(data)

        except requests.exceptions.ConnectionError:
            loading_ring.visible = False
            error_banner.visible = True
            error_text.value = "Could not connect to the server. Is it running?"
            page.update()

        except requests.exceptions.Timeout:
            loading_ring.visible = False
            error_banner.visible = True
            error_text.value = "Request timed out. Please try again."
            page.update()

        except Exception as exc:
            loading_ring.visible = False
            error_banner.visible = True
            error_text.value = f"Unexpected error: {exc}"
            page.update()

    cached_data = page.session.store.get(CACHE_KEY)
    if cached_data:
        populate_sections(cached_data)
    else:
        page.run_task(load_catalogue)

    inner = ft.Column(
        controls=[
            build_hero_banner(),
            error_banner,
            loading_ring,
            content_col,
            ft.Container(height=80),                     # FIX 1: nav bar spacer
        ],
        spacing=20,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    return ft.Container(
        content=inner,
        padding=ft.padding.symmetric(horizontal=12, vertical=14),
        expand=True,
    )


activities_page = catalogue_view