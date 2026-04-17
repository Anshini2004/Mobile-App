"""
home_screen.py
──────────────
Fetches GET /api/activities/   (ActivityListSerializer)
Returns: id, name, location, activity_type, base_price,
         duration, max_participants, avg_rating, images[{image_url}]

Tapping a card → page.go(f"/activity/{id}")
"""

import flet as ft
import threading
import requests

# BASE_URL = "http://127.0.0.1:8000"
BASE_URL = "http://192.168.100.10:8000"

TEAL   = "#2CBFB1"
BG     = "#FFFFFF"
TEXT   = "#1A1A1A"
MUTED  = "#9E9E9E"
BORDER = "#EFEFEF"
AMBER  = "#FFC107"
RED    = "#D32F2F"

TYPE_EMOJI = {
    "Catamaran":        "⛵",
    "Scuba diving":     "🤿",
    "Dolphin watching": "🐬",
    "Water ski":        "🎿",
    "Speed boat":       "🚤",
}


def home_view(page: ft.Page):

    scroll_col = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        spacing=0,
        expand=True,
    )

    scroll_col.controls = [
        ft.Container(
            height=600,
            alignment=ft.Alignment(0, 0),
            content=ft.Column(
                [ft.ProgressRing(color=TEAL),
                 ft.Text("Loading activities…", color=MUTED, size=13)],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=14,
            ),
        )
    ]

    # ── Single activity card ──────────────────────────────────────
    def activity_card(activity: dict) -> ft.Container:
        aid        = activity.get("id")
        name       = activity.get("name", "")
        atype      = activity.get("activity_type", "")
        price      = activity.get("base_price", 0)
        location   = activity.get("location", "")
        duration   = activity.get("duration", "")
        avg_rating = activity.get("avg_rating") or 0.0
        images     = activity.get("images", [])
        img_url    = images[0].get("image_url") if images else None
        emoji      = TYPE_EMOJI.get(atype, "🌊")

        full = int(avg_rating)
        stars = ft.Row(
            spacing=1,
            controls=[
                ft.Icon(ft.Icons.STAR, color=AMBER, size=11)
                for _ in range(full)
            ] + [
                ft.Icon(ft.Icons.STAR_BORDER, color=AMBER, size=11)
                for _ in range(5 - full)
            ],
        )

        if img_url:
            hero_content = ft.Image(
                src=img_url, fit="cover", expand=True,
                error_content=ft.Container(
                    expand=True, bgcolor="#B2EBF2",
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text(emoji, size=40),
                ),
            )
        else:
            hero_content = ft.Container(
                expand=True, bgcolor="#B2EBF2",
                alignment=ft.Alignment(0, 0),
                content=ft.Text(emoji, size=40),
            )

        return ft.Container(
            bgcolor=BG,
            border_radius=16,
            border=ft.Border.all(1, BORDER),
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            on_click=lambda _, _id=aid: page.go(f"/activity/{_id}"),
            shadow=ft.BoxShadow(
                blur_radius=8, spread_radius=0,
                color=ft.Colors.with_opacity(0.07, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
            content=ft.Column(
                spacing=0,
                controls=[
                    ft.Container(height=160, content=hero_content),
                    ft.Container(
                        padding=ft.padding.symmetric(horizontal=14, vertical=12),
                        content=ft.Column(
                            spacing=6,
                            controls=[
                                ft.Text(name, size=14,
                                        weight=ft.FontWeight.BOLD,
                                        color=TEXT, max_lines=1,
                                        overflow=ft.TextOverflow.ELLIPSIS),
                                ft.Row(spacing=4, controls=[
                                    ft.Icon(ft.Icons.LOCATION_ON,
                                            size=11, color=TEAL),
                                    ft.Text(location, size=11, color=MUTED,
                                            max_lines=1,
                                            overflow=ft.TextOverflow.ELLIPSIS,
                                            expand=True),
                                ]),
                                ft.Row(spacing=4, controls=[
                                    stars,
                                    ft.Text(
                                        f"  {avg_rating:.1f}"
                                        if avg_rating else "  No ratings",
                                        size=11, color=MUTED),
                                ]),
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Row(spacing=4, controls=[
                                            ft.Icon(ft.Icons.TIMELAPSE,
                                                    size=11, color=MUTED),
                                            ft.Text(duration, size=11,
                                                    color=MUTED),
                                        ]),
                                        ft.Container(
                                            bgcolor=TEAL, border_radius=20,
                                            padding=ft.padding.symmetric(
                                                horizontal=10, vertical=4),
                                            content=ft.Text(
                                                f"Rs {price:,}", size=12,
                                                color="white",
                                                weight=ft.FontWeight.BOLD),
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        )

    def section_header(title: str) -> ft.Row:
        return ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text(title, size=16,
                        weight=ft.FontWeight.BOLD, color=TEXT),
                ft.Text("See all", size=12, color=TEAL),
            ],
        )

    # ── Build page once data arrives ──────────────────────────────
    def build_page(activities: list):
        if not activities:
            scroll_col.controls = [
                ft.Container(
                    height=400, alignment=ft.Alignment(0, 0),
                    content=ft.Column(
                        [ft.Icon(ft.Icons.SAILING, size=60, color=MUTED),
                         ft.Text("No activities found.", color=MUTED, size=13)],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=14,
                    ),
                )
            ]
            return

        # group by type
        grouped: dict = {}
        for a in activities:
            atype = a.get("activity_type") or "Other"
            grouped.setdefault(atype, []).append(a)

        sections = []

        # hero banner
        sections.append(
            ft.Container(
                height=180, bgcolor=TEAL,
                content=ft.Stack(
                    expand=True,
                    controls=[
                        ft.Container(
                            expand=True,
                            gradient=ft.LinearGradient(
                                begin=ft.alignment.Alignment(-1, -1),
                                end=ft.alignment.Alignment(1, 1),
                                colors=["#2CBFB1", "#1A8C82"],
                            ),
                        ),
                        ft.Container(
                            expand=True,
                            padding=ft.padding.symmetric(horizontal=24, vertical=28),
                            content=ft.Column(spacing=6, controls=[
                                ft.Text("Grand Blue 🌊", size=26,
                                        weight=ft.FontWeight.BOLD,
                                        color="white"),
                                ft.Text("Above & Below Sea Level",
                                        size=13, color="#FFFFFFCC"),
                                ft.Container(height=4),
                                ft.Container(
                                    bgcolor="#FFFFFF22", border_radius=20,
                                    padding=ft.padding.symmetric(
                                        horizontal=14, vertical=6),
                                    width=180,
                                    content=ft.Text(
                                        f"{len(activities)} activities available",
                                        size=12, color="white"),
                                ),
                            ]),
                        ),
                    ],
                ),
            )
        )

        sections.append(ft.Container(height=4))

        # one horizontal scroll row per activity type
        for atype, acts in grouped.items():
            emoji = TYPE_EMOJI.get(atype, "🌊")
            sections.append(
                ft.Container(
                    padding=ft.padding.only(left=16, top=16, right=16, bottom=4),
                    content=section_header(f"{emoji}  {atype}"),
                )
            )
            sections.append(
                ft.Container(
                    padding=ft.padding.only(left=16, bottom=8),
                    content=ft.Row(
                        scroll=ft.ScrollMode.AUTO,
                        spacing=12,
                        controls=[
                            ft.Container(width=200, content=activity_card(a))
                            for a in acts
                        ],
                    ),
                )
            )

        sections.append(ft.Container(height=20))
        scroll_col.controls = sections

    # ── Fetch ─────────────────────────────────────────────────────
    def fetch():
        try:
            resp = requests.get(f"{BASE_URL}/api/activities/", timeout=10)
            resp.raise_for_status()
            data = resp.json()
            activities = data if isinstance(data, list) else data.get("results", [])
            build_page(activities)
        except requests.ConnectionError:
            _show_error("Cannot connect to server.\nMake sure Django is running.")
        except requests.HTTPError as exc:
            _show_error(f"Server error {exc.response.status_code}")
        except Exception as exc:
            _show_error(str(exc))
        page.update()

    def _show_error(msg: str):
        scroll_col.controls = [
            ft.Container(
                height=600, alignment=ft.Alignment(0, 0),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=14,
                    controls=[
                        ft.Icon(ft.Icons.ERROR_OUTLINE, color=RED, size=48),
                        ft.Text(msg, color=MUTED, size=13,
                                text_align=ft.TextAlign.CENTER),
                        ft.TextButton(
                            "Retry",
                            on_click=lambda e: page.run_thread(fetch)),
                    ],
                ),
            )
        ]

    page.run_thread(fetch)

    return ft.View(
        route="/",
        bgcolor=BG,
        padding=0,
        appbar=ft.AppBar(
            title=ft.Text("Grand Blue", color="white",
                          weight=ft.FontWeight.BOLD, size=18),
            bgcolor=TEAL,
            elevation=0,
            center_title=False,
        ),
        controls=[ft.Container(expand=True, content=scroll_col)],
    )