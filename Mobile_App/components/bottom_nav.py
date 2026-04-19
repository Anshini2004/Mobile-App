import flet as ft


def bottom_nav(page: ft.Page, active_route: str):
    PRIMARY = "#1D9FA5"
    PRIMARY_SOFT = "#D9F3F4"
    CARD = "#FFFFFF"
    BORDER = "#D7E8EA"
    TEXT_MUTED = "#6D8790"

    def nav_item(icon_name, label, route):
        selected = active_route == route

        def go_route(e):
            page.run_task(page.push_route, route)

        return ft.Container(
            expand=True,
            height=74,
            padding=ft.Padding.symmetric(horizontal=2, vertical=6),
            bgcolor=PRIMARY_SOFT if selected else "transparent",
            border_radius=18,
            ink=True,
            on_click=go_route,
            content=ft.Column(
                controls=[
                    ft.Icon(
                        icon_name,
                        size=22,
                        color=PRIMARY if selected else TEXT_MUTED,
                    ),
                    ft.Text(
                        label,
                        size=10,
                        color=PRIMARY if selected else TEXT_MUTED,
                        weight=ft.FontWeight.W_600 if selected else ft.FontWeight.W_400,
                        text_align=ft.TextAlign.CENTER,
                        max_lines=1,
                        no_wrap=True,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                ],
                spacing=4,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

    return ft.Container(
        left=10,
        right=10,
        bottom=10,
        padding=8,
        bgcolor=CARD,
        border_radius=26,
        border=ft.border.all(1, BORDER),
        content=ft.Row(
            controls=[
                nav_item(ft.Icons.GRID_VIEW_OUTLINED, "Catalogue", "/home"),
                nav_item(ft.Icons.PLACE_OUTLINED, "Near Me", "/near_us"),
                nav_item(ft.Icons.CALENDAR_MONTH_OUTLINED, "Bookings", "/bookings"),
                nav_item(ft.Icons.PERSON_OUTLINE, "Profile", "/profile"),
            ],
            spacing=4,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )