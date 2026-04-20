import flet as ft


def splash_view(page: ft.Page):

    # ---------------------------
    # NAVIGATION FUNCTIONS
    # ---------------------------
    def go_home(e):
        page.run_task(page.push_route, "/home")

    def go_login(e):
        page.run_task(page.push_route, "/login")

    def go_register(e):
        page.run_task(page.push_route, "/register")

    # ---------------------------
    # BUTTON
    # ---------------------------
    button = ft.Container(
        content=ft.Text(
            "Discover",
            color="black",
            size=16,
            weight=ft.FontWeight.W_600,
        ),
        height=55,
        width=200,
        border_radius=30,
        bgcolor="#EDEDED",
        alignment=ft.alignment.Alignment(0, 0),
        on_click=go_home,
    )

    # ---------------------------
    # VIEW
    # ---------------------------
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

                    # BACKGROUND IMAGE
                    ft.Image(
                        src="splash.jpg",
                        fit="cover",
                        expand=True,
                        width=float("inf"),
                        height=float("inf"),
                    ),

                    # DARK OVERLAY
                    ft.Container(
                        expand=True,
                        bgcolor="#55000000",
                    ),

                    # CONTENT
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

                                # LOGIN / REGISTER
                                ft.Container(
                                    width=200,
                                    alignment=ft.alignment.Alignment(0, 0),
                                    content=ft.Row(
                                        [
                                            ft.Container(
                                                width=80,
                                                alignment=ft.alignment.Alignment(-1, 0),
                                                content=ft.TextButton(
                                                    "Log In",
                                                    on_click=go_login,
                                                    style=ft.ButtonStyle(color="white70"),
                                                ),
                                            ),

                                            ft.Text("·", color="white54", size=16),

                                            ft.Container(
                                                width=80,
                                                alignment=ft.alignment.Alignment(1, 0),
                                                content=ft.TextButton(
                                                    "Sign Up",
                                                    on_click=go_register,
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