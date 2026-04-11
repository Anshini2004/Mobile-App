import flet as ft
from components.bottom_nav import bottom_nav


def home_view(page: ft.Page, active_route: str):
    BG = "#F4FBFC"
    CARD = "#FFFFFF"
    PRIMARY = "#1D9FA5"
    PRIMARY_DARK = "#13777B"
    PRIMARY_SOFT = "#D9F3F4"
    TEXT = "#17323B"
    TEXT_MUTED = "#6D8790"
    BORDER = "#D7E8EA"

    page_titles = {
        "/home": "Home",
        "/near_us": "Near Us",
        "/bookings": "Bookings",
        "/profile": "Profile",
    }

    page_subtitles = {
        "/home": "Temporary homepage for testing after login.",
        "/near_us": "Temporary Near Us page.",
        "/bookings": "Temporary Bookings page.",
        "/profile": "Temporary Profile page.",
    }

    display_name = page.session.store.get("user_name") or "Guest"
    username_text = page.session.store.get("user_username") or "Guest"
    user_email = page.session.store.get("user_email") or "N/A"

    async def logout_user(e):
        for key in ["user_name", "user_username", "user_email", "user_id", "user_data", "access_token", "refresh_token"]:
            if page.session.store.contains_key(key):
                page.session.store.remove(key)
        await page.push_route("/")

    content = ft.Container(
        expand=True,
        padding=ft.padding.only(left=22, right=22, top=26, bottom=145),
        content=ft.Column(
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(
                            spacing=3,
                            controls=[
                                ft.Text(
                                    f"Welcome, {display_name}",
                                    size=28,
                                    weight=ft.FontWeight.BOLD,
                                    color=TEXT,
                                ),
                                ft.Text(
                                    f"Logged in as: {username_text}",
                                    size=13,
                                    color=TEXT_MUTED,
                                ),
                            ],
                        ),
                        ft.Container(
                            width=52,
                            height=52,
                            border_radius=16,
                            bgcolor=PRIMARY_SOFT,
                            content=ft.Icon(ft.Icons.PERSON, color=PRIMARY_DARK, size=28),
                        ),
                    ],
                ),
                ft.Container(height=18),
                ft.Container(
                    width=470,
                    bgcolor=PRIMARY,
                    border_radius=28,
                    padding=20,
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                page_titles.get(active_route, "Home"),
                                size=22,
                                weight=ft.FontWeight.BOLD,
                                color="white",
                            ),
                            ft.Text(
                                page_subtitles.get(active_route, "Temporary page."),
                                size=13,
                                color="#E8FFFF",
                            ),
                        ],
                        spacing=10,
                    ),
                ),
                ft.Container(height=18),
                ft.Container(
                    width=470,
                    bgcolor=CARD,
                    border_radius=24,
                    border=ft.border.all(1, BORDER),
                    padding=20,
                    content=ft.Column(
                        spacing=10,
                        controls=[
                            ft.Text(
                                "Temporary Logged-in User Info",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=TEXT,
                            ),
                            ft.Text(f"Name: {display_name}", size=14, color=TEXT),
                            ft.Text(f"Username: {username_text}", size=14, color=TEXT),
                            ft.Text(f"Email: {user_email}", size=14, color=TEXT),
                            ft.Container(height=4),
                            ft.ElevatedButton(
                                "Log out",
                                icon=ft.Icons.LOGOUT,
                                style=ft.ButtonStyle(
                                    bgcolor=PRIMARY_SOFT,
                                    color=PRIMARY_DARK,
                                    shape=ft.RoundedRectangleBorder(radius=14),
                                ),
                                on_click=logout_user,
                            ),
                        ],
                    ),
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
        ),
    )

    return ft.View(
        route=active_route,
        bgcolor=BG,
        controls=[
            ft.Stack(
                expand=True,
                controls=[
                    content,
                    bottom_nav(page, active_route),
                ],
            )
        ],
    )