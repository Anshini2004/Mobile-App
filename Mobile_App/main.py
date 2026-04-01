import flet as ft
from views.payment_view import payment_view
from views.success_view import success_view


async def main(page: ft.Page):

    page.title = "Payment App"
    page.bgcolor = "#F7F9FC"

    #  apply window settings AFTER load
    async def setup_window():
        page.window.width = 550
        page.window.height = 900
        page.window.resizable = False
        page.window.maximizable = False
       

    booking_data = {
        "activity_id": 7,
        "activity_name": "Catamaran Sunset Serenity",
        "date": "2026-04-10",
        "num_people": 2,
        "total_price": 2600,
    }

    async def on_route_change(e):
        page.views.clear()

        if page.route.startswith("/success"):
            booking_id = page.route.split("/")[-1]
            page.views.append(success_view(page, booking_id))

        elif page.route == "/payment":
            page.views.append(payment_view(page, booking_data))

        await setup_window()   # APPLY SIZE HERE
        page.update()

    page.on_route_change = on_route_change

    # start app
    await page.push_route("/payment")


ft.run(main)