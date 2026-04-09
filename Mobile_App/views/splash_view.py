import flet as ft
import asyncio


def splash_view(page: ft.Page):

    button = ft.Container()

    async def handle_click(e):
        page.go("/home")

    button.content = ft.Text(
        "Discover",
        color="black",
        size=16,
        weight=ft.FontWeight.W_600,
    )
    button.height = 55
    button.width = 200
    button.border_radius = 30
    button.bgcolor = "#EDEDED"
    button.alignment = ft.alignment.Alignment(0, 0)
    button.on_click = handle_click

    return ft.View(
        route="/",
        expand=True,
        padding=0,
        bgcolor="#000000",
        controls=[
            ft.Stack(
                expand=True,
                fit=ft.StackFit.EXPAND,
                controls=[

                    # 🖼️ BACKGROUND IMAGE
                    ft.Image(
                        src="splash.jpg",
                        fit="cover",  # ✅ correct for old versions
                        expand=True,
                        width=float("inf"),
                        height=float("inf"),
                    ),

                    # 🌑 DARK OVERLAY
                    ft.Container(
                        expand=True,
                        bgcolor="#55000000",
                    ),

                    # 📄 CONTENT
                    ft.Container(
                        expand=True,
                        padding=ft.padding.only(left=30, right=30, bottom=40),
                        content=ft.Column(
                            [
                                ft.Container(expand=250),

                                ft.Text(
                                    "Get ready for",
                                    size=16,
                                    color="white",
                                    text_align=ft.TextAlign.CENTER,
                                ),

                                ft.Text(
                                    "New Adventures",
                                    size=32,
                                    weight=ft.FontWeight.BOLD,
                                    color="white",
                                    text_align=ft.TextAlign.CENTER,
                                ),

                                ft.Text(
                                    "Discover breathtaking marine experiences! "
                                    "Here you can explore the beauty of the world.",
                                    size=14,
                                    color="white70",
                                    text_align=ft.TextAlign.CENTER,
                                ),

                                ft.Container(height=24),

                                ft.Row(
                                    [button],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                ),

                                ft.Container(height=10),

                                # ✅ OLD VERSION FRIENDLY LOGIN ROW
                                ft.Container(
                                    width=200,  # same as button
                                    alignment=ft.alignment.Alignment(0, 0),
                                    content=ft.Row(
                                        [
                                            # LEFT SIDE
                                            ft.Container(
                                                width=80,
                                                alignment=ft.alignment.Alignment(-1, 0),
                                                content=ft.TextButton(
                                                    "Log In",
                                                    on_click=lambda e: page.go("/login"),
                                                    style=ft.ButtonStyle(color="white70"),
                                                ),
                                            ),

                                            # CENTER DOT
                                            ft.Text("·", color="white54", size=16),

                                            # RIGHT SIDE
                                            ft.Container(
                                                width=130,
                                                alignment=ft.alignment.Alignment(1, 0),
                                                content=ft.TextButton(
                                                    "Create Account",
                                                    on_click=lambda e: page.go("/register"),
                                                    style=ft.ButtonStyle(color="white70"),
                                                ),
                                            ),
                                        ],
                                        alignment=ft.MainAxisAlignment.CENTER,
                                    ),
                                ),

                                ft.Container(height=20),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    ),
                ],
            )
        ],
    )