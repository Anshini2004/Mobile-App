import flet as ft
import requests
import re
from datetime import datetime
import asyncio

BASE_URL = "http://127.0.0.1:8000"


def payment_view(page: ft.Page):
    booking_data = page.session.store.get("booking_data") or {}

    activity_name = booking_data.get("activity_name", "Activity")
    activity_id = booking_data.get("activity_id", "")
    book_date = booking_data.get("date", "")
    book_time = booking_data.get("time", "")
    num_people = booking_data.get("num_people", 1)
    total_price = booking_data.get("total_price", 0)

    PRIMARY = "#0A2540"
    BG = "#F5F5F5"
    CARD = "#FFFFFF"
    BORDER = "#E0E0E0"
    TEXT_MUTED = "#2E2E2E"

    def go_back(e):
        if activity_id:
            page.run_task(page.push_route, f"/activity/{activity_id}")
        else:
            page.run_task(page.push_route, "/")

    def section(title, content):
        return ft.Container(
            bgcolor=CARD,
            border_radius=14,
            border=ft.border.all(1, BORDER),
            padding=16,
            content=ft.Column(
                [
                    ft.Text(
                        title.upper(),
                        size=11,
                        weight=ft.FontWeight.BOLD,
                        color=TEXT_MUTED,
                    ),
                    ft.Container(height=10),
                    content,
                ],
                spacing=0,
            ),
        )

    def input_field(label, hint, width=None):
        return ft.TextField(
            label=label,
            hint_text=hint,
            width=width,
            height=50,
            border_radius=10,
            border_color=BORDER,
            focused_border_color=PRIMARY,
            bgcolor="#FAFAFA",
            color="#000000",
        )

    def method(image_url, selected=False):
        return ft.Container(
            expand=True,
            height=50,
            border_radius=10,
            bgcolor="#EAF1FF" if selected else "#F2F2F2",
            border=ft.border.all(1.5, PRIMARY if selected else BORDER),
            alignment=ft.alignment.Alignment(0, 0),
            content=ft.Image(
                src=image_url,
                width=36,
                height=24,
                fit="contain",
            ),
        )

    methods = ft.Row(
        [
            method("https://cdn-icons-png.flaticon.com/512/196/196578.png"),
            method("https://cdn-icons-png.flaticon.com/512/196/196561.png"),
            method("https://cdn-icons-png.flaticon.com/512/174/174861.png"),
        ],
        spacing=10,
    )

    step_bar = ft.Row(
        [
            ft.Row(
                [
                    ft.Container(
                        width=30,
                        height=30,
                        border_radius=15,
                        bgcolor=PRIMARY,
                        alignment=ft.alignment.Alignment(0, 0),
                        content=ft.Text("1", color="white"),
                    ),
                    ft.Text("Payment", color=TEXT_MUTED),
                ],
                spacing=8,
            ),
            ft.Container(expand=True, height=1, bgcolor=BORDER),
            ft.Row(
                [
                    ft.Container(
                        width=30,
                        height=30,
                        border_radius=15,
                        border=ft.border.all(1, BORDER),
                        alignment=ft.alignment.Alignment(0, 0),
                        content=ft.Text("2", color=TEXT_MUTED),
                    ),
                    ft.Text("Confirm", color=TEXT_MUTED),
                ],
                spacing=8,
            ),
        ],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    card_number = input_field("Card number", "1234 5678 9012 3456")
    card_name = input_field("Cardholder name", "Full name as on card")
    expiry = input_field("MM / YY", "Expiry Date", 150)
    cvv = input_field("CVV", "•••", 120)

    def format_card(e):
        raw = re.sub(r"\D", "", e.control.value or "")[:16]
        e.control.value = " ".join(raw[i:i + 4] for i in range(0, len(raw), 4))
        e.control.update()

    def format_expiry(e):
        raw = re.sub(r"\D", "", e.control.value or "")[:4]
        e.control.value = raw[:2] + "/" + raw[2:] if len(raw) >= 3 else raw
        e.control.update()

    def format_cvv(e):
        e.control.value = re.sub(r"\D", "", e.control.value or "")[:3]
        e.control.update()

    card_number.on_change = format_card
    expiry.on_change = format_expiry
    cvv.on_change = format_cvv

    def validate():
        card_number.error_text = None
        card_name.error_text = None
        expiry.error_text = None
        cvv.error_text = None

        if not card_name.value or not re.fullmatch(r"[A-Za-z ]+", card_name.value.strip()):
            card_name.error_text = "Enter valid name"
            return "Cardholder name is invalid"

        number = (card_number.value or "").replace(" ", "")
        if not number.isdigit() or len(number) != 16:
            card_number.error_text = "Must be 16 digits"
            return "Card number must be 16 digits"

        if not cvv.value or not cvv.value.isdigit() or len(cvv.value) != 3:
            cvv.error_text = "3 digits"
            return "CVV must be 3 digits"

        try:
            mm, yy = expiry.value.split("/")
            month = int(mm.strip())
            year = int("20" + yy.strip())
            now = datetime.now()

            if month < 1 or month > 12:
                expiry.error_text = "MM/YY"
                return "Expiry must be in MM/YY format"

            if year < now.year or (year == now.year and month < now.month):
                expiry.error_text = "Expired"
                return "Card expiry date is invalid or expired"
        except Exception:
            expiry.error_text = "MM/YY"
            return "Expiry must be in MM/YY format"

        return None

    def show_error(message):
        snack = ft.SnackBar(content=ft.Text(message), bgcolor="#D32F2F")
        page.overlay.append(snack)
        snack.open = True
        page.update()

    async def handle_payment(e):
        error = validate()
        card_number.update()
        card_name.update()
        expiry.update()
        cvv.update()

        if error:
            show_error(error)
            return

        processing_snack = ft.SnackBar(
            content=ft.Text("Processing payment..."),
            bgcolor=PRIMARY,
        )
        page.overlay.append(processing_snack)
        processing_snack.open = True
        page.update()

        try:
            resp = await asyncio.to_thread(
                requests.post,
                f"{BASE_URL}/api/payments/",
                json={
                    "activity_id": activity_id,
                    "booking_date": book_date,
                    "num_people": num_people,
                    "amount": total_price,          # ✅ FIX: added missing field
                    "card_number": card_number.value,
                    "card_name": card_name.value.strip(),
                    "expiry_date": expiry.value.strip(),
                    "cvv": cvv.value,
                },
                timeout=15,
            )

            try:
                data = resp.json()
            except Exception:
                data = {}

            if resp.status_code == 200 and data.get("status") == "success":
                if page.session.store.contains_key("booking_data"):
                    page.session.store.remove("booking_data")

                booking_id = str(data.get("booking_id", ""))
                await page.push_route(f"/success/{booking_id}")
            else:
                err_msg = data.get("error") or str(data.get("errors", "Payment failed."))
                show_error(err_msg)

        except requests.ConnectionError:
            show_error("Cannot connect to server.")
        except Exception as ex:
            show_error(str(ex))

    card_section = section(
        "Card details",
        ft.Column(
            [
                card_number,
                card_name,
                ft.Row([expiry, cvv], spacing=10),
            ],
            spacing=10,
        ),
    )

    def row(label, value, bold=False):
        return ft.Row(
            [
                ft.Text(label, color=TEXT_MUTED),
                ft.Text(
                    value,
                    color="#000000",
                    weight=ft.FontWeight.BOLD if bold else None,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

    summary = section(
        "Order summary",
        ft.Column(
            [
                row("Activity", activity_name),
                row("Date", str(book_date)),
                row("Guests", f"{num_people} people"),
                ft.Divider(),
                row("Total", f"Rs {total_price}", True),
            ],
            spacing=8,
        ),
    )

    pay_button = ft.Container(
        height=55,
        border_radius=12,
        bgcolor=PRIMARY,
        alignment=ft.alignment.Alignment(0, 0),
        on_click=handle_payment,
        content=ft.Text(
            "Confirm & pay →",
            color="white",
            size=16,
            weight=ft.FontWeight.W_600,
        ),
    )

    return ft.View(
        route="/payment",
        bgcolor=BG,
        controls=[
            ft.Container(
                expand=True,
                content=ft.Column(
                    [
                        ft.Container(
                            padding=20,
                            content=ft.Column(
                                [
                                    ft.Row(
                                        [
                                            ft.TextButton("← Back", on_click=go_back)
                                        ]
                                    ),
                                    ft.Text("CHECKOUT", size=12, color=TEXT_MUTED),
                                    ft.Text(
                                        "Complete your booking",
                                        size=22,
                                        weight=ft.FontWeight.BOLD,
                                        color="#000000",
                                    ),
                                    step_bar,
                                    section("Payment method", methods),
                                    card_section,
                                    summary,
                                    pay_button,
                                ],
                                spacing=18,
                            ),
                        )
                    ],
                    scroll=ft.ScrollMode.AUTO,
                ),
            )
        ],
    )