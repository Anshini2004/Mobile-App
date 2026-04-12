import flet as ft
from views.login_view import login_view
from views.register_view import register_view
from views.home_view import home_view


def main(page: ft.Page):
    page.title = "Grand Blue"
    page.bgcolor = "#000000"
    page.padding = 0
    page.spacing = 0

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

    page.window.width = 550
    page.window.height = 900
    page.window.resizable = False
    page.window.maximizable = False
    page.window.bgcolor = "#000000"

    def is_authenticated():
        access_token = page.session.store.get("access_token")
        user_name = page.session.store.get("user_username")
        return bool(access_token and user_name)

    def show_logged_in_view(route: str):
        page.views.append(home_view(page, route))

    def route_change(e: ft.RouteChangeEvent):
        route = e.route
        page.views.clear()

        if route == "/":
            if is_authenticated():
                show_logged_in_view("/home")
            else:
                page.views.append(login_view(page))

        elif route == "/register":
            page.views.append(register_view(page))

        elif route in ["/home", "/near_us", "/bookings", "/profile"]:
            if is_authenticated():
                show_logged_in_view(route)
            else:
                page.views.append(login_view(page))

        else:
            if is_authenticated():
                show_logged_in_view("/home")
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
                show_logged_in_view("/home")
            else:
                page.views.append(login_view(page))
            page.update()

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    if is_authenticated():
        page.views.append(home_view(page, "/home"))
    else:
        page.views.append(login_view(page))

    page.update()


ft.run(main)