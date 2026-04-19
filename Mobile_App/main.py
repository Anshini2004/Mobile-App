import flet as ft

from views.shreeyash_home_screen import home_view
from views.activity_detail_view import activity_detail_view
from views.payment_view import payment_view
from views.success_view import success_view
from views.splash_view import splash_view

# NEW PAGES
from views.nearme import main as nearme_view
from views.profile import profile_view


def main(page: ft.Page):
    page.title = "Grand Blue"
    page.bgcolor = "#000000"
    page.padding = 0
    page.spacing = 0
    page.window.width = 550
    page.window.height = 800
    page.window.resizable = False
    page.window.maximizable = False
    page.window.bgcolor = "#000000"

    # ─────────────────────────────────────────────
    # ROUTING
    # ─────────────────────────────────────────────
    def route_change(e: ft.RouteChangeEvent):
        route = e.route
        page.views.clear()

        # Splash
        if route == "/":
            page.views.append(splash_view(page))

        # Home
        elif route == "/home":
            page.views.append(home_view(page))

        # Near Me (MAP PAGE)
        elif route == "/nearme":
            page.views.append(ft.View(
                "/nearme",
                controls=[ft.Container(expand=True, content=nearme_view)]
            ))

        # Profile
        elif route == "/profile":
            page.views.append(ft.View(
                "/profile",
                controls=[profile_view(page)]
            ))

        # Activity details
        elif route.startswith("/activity/"):
            try:
                activity_id = int(route.split("/activity/")[1])
                page.views.append(activity_detail_view(page, activity_id))
            except (ValueError, IndexError):
                page.views.append(home_view(page))

        # Payment
        elif route == "/payment":
            if not page.session.store.contains_key("booking_data"):
                page.views.append(home_view(page))
            else:
                page.views.append(payment_view(page))

        # Success
        elif route.startswith("/success/"):
            try:
                booking_id = route.split("/success/")[1]
                page.views.append(success_view(page, booking_id))
            except IndexError:
                page.views.append(home_view(page))

        # fallback
        else:
            page.views.append(home_view(page))

        page.update()

    # ─────────────────────────────────────────────
    # BACK BUTTON HANDLING
    # ─────────────────────────────────────────────
    def view_pop(e: ft.ViewPopEvent):
        page.views.pop()
        if page.views:
            page.update()
        else:
            page.views.append(home_view(page))
            page.update()

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # initial view
    page.views.append(splash_view(page))
    page.update()


ft.app(
    target=main,
    assets_dir="assets",
    host="0.0.0.0",
    port=8550
)