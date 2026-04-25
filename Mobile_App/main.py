import flet as ft

# views
from views.splash_view import splash_view
from views.login_view import login_view
from views.register_view import register_view
from views.catalogue_view import catalogue_view
from views.activity_detail_view import activity_detail_view
from views.payment_view import payment_view
from views.success_view import success_view
from views.booking_view import bookings_page
import views.profile as profile_view
from components.bottom_nav import bottom_nav
from views.nearme import nearme_view


def main(page: ft.Page):
    page.title = "Grand Blue"
    page.padding = 0
    page.spacing = 0

    page.bgcolor = "#000000"

    page.window.width = 550
    page.window.height = 900
    page.window.resizable = False
    page.window.maximizable = False
    page.window.bgcolor = "#000000"

    page.window.always_on_top = True

    page.update()

    # AUTH CHECK
    def is_authenticated():
        return page.session.store.get("access_token") is not None

    # ROUTER
    def route_change(e):
        print("ROUTE:", e.route)
        page.views.clear()

        if e.route == "/":
            view = splash_view(page)

        elif e.route == "/login":
            view = login_view(page)

        elif e.route == "/register":
            view = register_view(page)

        elif e.route == "/home":
            view = ft.View(
                route="/home",
                controls=[
                    ft.Stack(
                        expand=True,
                        controls=[
                            catalogue_view(page),
                            bottom_nav(page, "/home"),
                        ],
                    )
                ],
            )

        elif e.route.startswith("/activity/"):
            activity_id = int(e.route.split("/")[-1])

            if not is_authenticated():
                page.go("/login")
                return

            view = activity_detail_view(page, activity_id)

        elif e.route == "/payment":
            if not is_authenticated():
                page.go("/login")
                return

            view = payment_view(page)

        elif e.route.startswith("/success/"):
            booking_id = e.route.split("/")[-1]
            view = success_view(page, booking_id)

        elif e.route == "/bookings":
            if not is_authenticated():
                page.go("/login")
                return

            user_id = page.session.store.get("user_id")  

            view = ft.View(
                route="/bookings",
                controls=[
                    ft.Stack(
                        expand=True,
                        controls=[
                            bookings_page(page),  
                            bottom_nav(page, "/bookings"),
                        ],
                    )
                ],
            )

        elif e.route == "/profile":
            if not is_authenticated():
                page.go("/login")
                return

            view = ft.View(
                route="/profile",
                controls=[
                    ft.Stack(
                        expand=True,
                        controls=[ 
                            profile_view.profile_view(page),
                            bottom_nav(page, "/profile"),
                        ],
                    )
                ],
            )
           

        elif e.route == "/near_us":
            view = ft.View(
                route="/near_us",
                controls=[
                    ft.Stack(
                        expand=True,
                        controls=[
                            nearme_view(page),
                            bottom_nav(page, "/near_us"),
                        ],
                    )
                ],
            )

        else:
            view = ft.View(
                route="/",
                controls=[ft.Text("Fallback — something broke", size=20)]
            )

        page.views.append(view)
        page.update()

    # BACK BUTTON
    def view_pop(e):
        page.views.pop()
        page.update()

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    page.views.append(splash_view(page))
    page.update()

    page.go("/")  # trigger routing


ft.run(main)