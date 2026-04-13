import flet as ft

from views.login_view import login_view
from views.register_view import register_view
from views.catalogue_view import catalogue_view
from components.bottom_nav import bottom_nav


def main(page: ft.Page):
    page.title = "Grand Blue"
    page.bgcolor = "#F4FBFC"
    page.padding = 0
    page.spacing = 0

    page.window.width = 550
    page.window.height = 900
    page.window.resizable = False
    page.window.maximizable = False
    page.window.bgcolor = "#F4FBFC"

    # Disable route transition animation
    page.theme = ft.Theme(
        page_transitions=ft.PageTransitionsTheme(
            android=ft.PageTransitionTheme.NONE,
            ios=ft.PageTransitionTheme.NONE,
            linux=ft.PageTransitionTheme.NONE,
            macos=ft.PageTransitionTheme.NONE,
            windows=ft.PageTransitionTheme.NONE,
        )
    )

    page.dark_theme = ft.Theme(
        page_transitions=ft.PageTransitionsTheme(
            android=ft.PageTransitionTheme.NONE,
            ios=ft.PageTransitionTheme.NONE,
            linux=ft.PageTransitionTheme.NONE,
            macos=ft.PageTransitionTheme.NONE,
            windows=ft.PageTransitionTheme.NONE,
        )
    )

    BG = "#F4FBFC"
    CARD = "#FFFFFF"
    PRIMARY = "#1D9FA5"
    PRIMARY_DARK = "#13777B"
    PRIMARY_SOFT = "#D9F3F4"
    TEXT = "#17323B"
    TEXT_MUTED = "#6D8790"
    BORDER = "#D7E8EA"

    def is_authenticated():
        access_token = page.session.store.get("access_token")
        user_name = page.session.store.get("user_username")
        return bool(access_token and user_name)

    def clear_auth_session():
        for key in [
            "user_name",
            "user_username",
            "user_email",
            "user_id",
            "user_data",
            "access_token",
            "refresh_token",
        ]:
            if page.session.store.contains_key(key):
                page.session.store.remove(key)

    def placeholder_card(title: str, subtitle: str):
        return ft.Container(
            width=470,
            bgcolor=CARD,
            border_radius=24,
            border=ft.border.all(1, BORDER),
            padding=20,
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Text(
                        title,
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=TEXT,
                    ),
                    ft.Text(
                        subtitle,
                        size=14,
                        color=TEXT_MUTED,
                    ),
                ],
            ),
        )

    async def logout_user(e):
        clear_auth_session()
        await page.push_route("/")

    def profile_content():
        display_name = page.session.store.get("user_name") or "Guest"
        username_text = page.session.store.get("user_username") or "Guest"
        user_email = page.session.store.get("user_email") or "N/A"

        return ft.Container(
            width=470,
            bgcolor=CARD,
            border_radius=24,
            border=ft.border.all(1, BORDER),
            padding=20,
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Text(
                        "Logged-in User Info",
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
        )

    def build_tab_shell(active_route: str) -> ft.View:
        # HOME: render catalogue directly + bottom nav
        if active_route == "/home":
            return ft.View(
                route="/home",
                bgcolor=BG,
                controls=[
                    ft.Stack(
                        expand=True,
                        controls=[
                            ft.Container(
                                expand=True,
                                padding=ft.Padding.only(left=0, right=0, top=0, bottom=110),
                                content=catalogue_view(page),
                            ),
                            bottom_nav(page, active_route),
                        ],
                    )
                ],
            )

        page_titles = {
            "/near_us": "Near Us",
            "/bookings": "Bookings",
            "/profile": "Profile",
        }

        page_subtitles = {
            "/near_us": "Discover nearby places and services.",
            "/bookings": "View and manage your bookings.",
            "/profile": "See your account details.",
        }

        display_name = page.session.store.get("user_name") or "Guest"
        username_text = page.session.store.get("user_username") or "Guest"

        if active_route == "/near_us":
            page_content = placeholder_card(
                "Near Us",
                "This section will show nearby places and related information.",
            )
        elif active_route == "/bookings":
            page_content = placeholder_card(
                "Bookings",
                "This section will show the user booking history and booking management.",
            )
        elif active_route == "/profile":
            page_content = profile_content()
        else:
            page_content = placeholder_card(
                "Page",
                "Content not found.",
            )

        content = ft.Container(
            expand=True,
            padding=ft.Padding.only(left=22, right=22, top=26, bottom=145),
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
                                content=ft.Icon(
                                    ft.Icons.PERSON,
                                    color=PRIMARY_DARK,
                                    size=28,
                                ),
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
                                    page_titles.get(active_route, "Page"),
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
                    page_content,
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

    def route_change(e: ft.RouteChangeEvent):
        route = e.route
        page.views.clear()

        if route == "/":
            if is_authenticated():
                page.views.append(build_tab_shell("/home"))
            else:
                page.views.append(login_view(page))

        elif route == "/register":
            page.views.append(register_view(page))

        elif route in ["/home", "/near_us", "/bookings", "/profile"]:
            if is_authenticated():
                page.views.append(build_tab_shell(route))
            else:
                page.views.append(login_view(page))

        else:
            if is_authenticated():
                page.views.append(build_tab_shell("/home"))
            else:
                page.views.append(login_view(page))

        page.update()

    def view_pop(e: ft.ViewPopEvent):
        if page.views:
            page.views.pop()

        if page.views:
            page.update()
        else:
            if is_authenticated():
                page.views.append(build_tab_shell("/home"))
            else:
                page.views.append(login_view(page))
            page.update()

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # Initial render
    if is_authenticated():
        page.views.append(build_tab_shell("/home"))
    else:
        page.views.append(login_view(page))

    page.update()


ft.run(main)