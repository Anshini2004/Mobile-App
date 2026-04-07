import flet as ft
import asyncio


def success_view(page, booking_id):
    PRIMARY = "#0A2540"
    BG = "#F5F5F5"
    CARD = "#FFFFFF"
    BORDER = "#E0E0E0"
    TEXT_MUTED = "#2E2E2E"

    def go_home(e):
        page.go("/")

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
                        content=ft.Text("✓", color="white", size=14),
                    ),
                    ft.Text("Payment", color=TEXT_MUTED),
                ],
                spacing=8,
            ),
            ft.Container(expand=True, height=2, bgcolor=PRIMARY),
            ft.Row(
                [
                    ft.Container(
                        width=30,
                        height=30,
                        border_radius=15,
                        bgcolor=PRIMARY,
                        alignment=ft.alignment.Alignment(0, 0),
                        content=ft.Text("2", color="white"),
                    ),
                    ft.Text("Confirm", color=PRIMARY),
                ],
                spacing=8,
            ),
        ],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    loading = ft.ProgressRing(width=40, height=40)

    icon_container = ft.Container(
        width=80,
        height=80,
        border_radius=40,
        bgcolor="#E3F2FD",
        alignment=ft.alignment.Alignment(0, 0),
        content=loading,
    )

    title_text = ft.Text(
        "Processing payment...",
        size=20,
        weight=ft.FontWeight.BOLD,
        color=PRIMARY,
    )

    booking_container = ft.Container(
        visible=False,
        padding=15,
        border_radius=10,
        bgcolor="#FAFAFA",
        border=ft.border.all(1, BORDER),
        content=ft.Column(
            [
                ft.Text("BOOKING ID", size=11, color=TEXT_MUTED),
                ft.Text(
                    str(booking_id),
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=PRIMARY,
                ),
            ],
            spacing=5,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    async def simulate():
        await asyncio.sleep(3)
        icon_container.bgcolor = "#E8F5E9"
        icon_container.content = ft.Icon(
            ft.Icons.CHECK,
            color="#2E7D32",
            size=40,
        )
        title_text.value = "Payment Successful"
        title_text.color = "#000000"
        booking_container.visible = True
        page.update()

    page.run_task(simulate)

    return ft.View(
        route=f"/success/{booking_id}",
        bgcolor=BG,
        controls=[
            ft.Container(
                expand=True,
                alignment=ft.alignment.Alignment(0, -1),
                padding=20,
                content=ft.Container(
                    width=380,
                    content=ft.Column(
                        [
                            
                            ft.Text("CHECKOUT", size=12, color=TEXT_MUTED),
                            ft.Text(
                                "Complete your booking",
                                size=22,
                                color=TEXT_MUTED,
                                weight=ft.FontWeight.BOLD,
                            ),
                            step_bar,
                            ft.Container(
                                bgcolor=CARD,
                                border_radius=14,
                                border=ft.border.all(1, BORDER),
                                padding=25,
                                content=ft.Column(
                                    [
                                        icon_container,
                                        title_text,
                                        ft.Text(
                                            "Your booking has been confirmed",
                                            size=14,
                                            color=TEXT_MUTED,
                                            text_align=ft.TextAlign.CENTER,
                                        ),
                                        ft.Container(height=10),
                                        booking_container,
                                        ft.Container(height=10),
                                        ft.Container(
                                            height=50,
                                            border_radius=12,
                                            bgcolor=PRIMARY,
                                            alignment=ft.alignment.Alignment(0, 0),
                                            on_click=go_home,
                                            content=ft.Text(
                                                "Back to Home",
                                                color="white",
                                                size=15,
                                                weight=ft.FontWeight.W_600,
                                            ),
                                        ),
                                    ],
                                    spacing=18,
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                            ),
                        ],
                        spacing=18,
                    ),
                ),
            )
        ],
    )