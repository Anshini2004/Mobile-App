import flet as ft
from views.shreeyash_home_screen import home_view
from views.activity_detail_view import activity_detail_view
from views.payment_view import payment_view
from views.success_view import success_view


def main(page: ft.Page):
    page.title = "Grand Blue"
    page.bgcolor = "#FFFFFF"
    page.padding = 0

    # same window size across whole app
    page.window.width = 550
    page.window.height = 900
    page.window.resizable = False
    page.window.maximizable = False

    def route_change(e: ft.RouteChangeEvent):
        route = e.route
        page.views.clear()

        if route == "/":
            page.views.append(home_view(page))

        elif route.startswith("/activity/"):
            try:
                activity_id = int(route.split("/activity/")[1])
                page.views.append(activity_detail_view(page, activity_id))
            except (ValueError, IndexError):
                page.views.append(home_view(page))

        elif route == "/payment":
            if not page.session.store.contains_key("booking_data"):
                page.views.append(home_view(page))
            else:
                page.views.append(payment_view(page))

        elif route.startswith("/success/"):
            try:
                booking_id = route.split("/success/")[1]
                page.views.append(success_view(page, booking_id))
            except IndexError:
                page.views.append(home_view(page))

        else:
            page.views.append(home_view(page))

        page.update()

    def view_pop(e: ft.ViewPopEvent):
        page.views.pop()
        if page.views:
            page.update()
        else:
            page.views.append(home_view(page))
            page.update()

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # important: keep this direct render for startup
    page.views.append(home_view(page))
    page.update()


ft.app(target=main)