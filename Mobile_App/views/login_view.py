import asyncio
import flet as ft

from utils.api_client import api_login, save_auth_session
from utils.activity_api import preload_activities


def login_view(page: ft.Page):
    BG = "#F4FBFC"
    CARD = "#FFFFFF"
    CARD_SOFT = "#ECF8F8"
    PRIMARY = "#1D9FA5"
    PRIMARY_DARK = "#13777B"
    PRIMARY_SOFT = "#D9F3F4"
    TEXT = "#17323B"
    TEXT_MUTED = "#6D8790"
    BORDER = "#D7E8EA"
    LINK = "#148E94"
    ERROR = "#C62828"
    SUCCESS = "#2E7D32"

    is_logging_in = False

    def show_message(message: str, color: str = PRIMARY_DARK):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color="white"),
            bgcolor=color,
            behavior=ft.SnackBarBehavior.FLOATING,
            show_close_icon=True,
        )
        page.snack_bar.open = True
        page.update()

    def input_field(label, hint="", password=False, icon=None, keyboard_type=None):
        return ft.TextField(
            label=label,
            hint_text=hint,
            password=password,
            can_reveal_password=password,
            prefix_icon=icon,
            keyboard_type=keyboard_type,
            width=420,
            border_color=BORDER,
            focused_border_color=PRIMARY,
            cursor_color=PRIMARY,
            filled=True,
            fill_color=CARD,
            text_size=14,
            color=TEXT,
        )

    email = input_field(
        "Email Address",
        "Enter your email",
        icon=ft.Icons.MAIL_OUTLINE,
        keyboard_type=ft.KeyboardType.EMAIL,
    )
    email_error = ft.Text("", size=11, color=ERROR, visible=False)

    password = input_field(
        "Password",
        "Enter your password",
        password=True,
        icon=ft.Icons.LOCK_OUTLINE,
    )
    password_error = ft.Text("", size=11, color=ERROR, visible=False)

    remember_me = ft.Checkbox(value=False, active_color=PRIMARY)
    form_error = ft.Text("", size=12, color=ERROR, text_align=ft.TextAlign.CENTER, visible=False)

    login_button_text = ft.Text(
        "Log In",
        color="white",
        size=16,
        weight=ft.FontWeight.BOLD,
    )

    login_button = ft.Container(
        width=420,
        height=54,
        bgcolor=PRIMARY,
        border_radius=18,
        ink=True,
        content=ft.Row(
            controls=[login_button_text],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
    )

    async def submit_login(e):
        nonlocal is_logging_in

        if is_logging_in:
            return

        is_logging_in = True
        login_button.on_click = None
        login_button.opacity = 0.7
        login_button_text.value = "Logging in..."
        page.update()

        email_error.value = ""
        email_error.visible = False
        password_error.value = ""
        password_error.visible = False
        form_error.value = ""
        form_error.visible = False
        page.update()

        result = await asyncio.to_thread(
            api_login,
            {
                "email": (email.value or "").strip(),
                "password": password.value or "",
            },
        )

        if result.get("fatal"):
            show_message(result["fatal"], ERROR)
            is_logging_in = False
            login_button.on_click = submit_login
            login_button.opacity = 1
            login_button_text.value = "Log In"
            page.update()
            return

        if result["ok"]:
            payload = result["data"]
            save_auth_session(page, payload)
            page.session.store.set("user_id", payload["user"]["id"])
            page.session.store.set("user_data", payload["user"])

            # Preload catalogue before routing to /home
            try:
                login_button_text.value = "Loading catalogue..."
                page.update()
                await asyncio.to_thread(preload_activities, page)
            except Exception:
                pass

            user = payload.get("user", {})
            show_message(
                f"Welcome, {user.get('full_name') or user.get('username') or user.get('email')}!",
                SUCCESS,
            )

            is_logging_in = False
            login_button.on_click = submit_login
            login_button.opacity = 1
            login_button_text.value = "Log In"
            page.update()

            await page.push_route("/home")
            return

        data = result.get("data", {})
        email_errors = data.get("email", [])
        password_errors = data.get("password", [])
        non_field_errors = data.get("non_field_errors", [])

        if email_errors:
            email_error.value = " ".join(email_errors)
            email_error.visible = True

        if password_errors:
            password_error.value = " ".join(password_errors)
            password_error.visible = True

        if non_field_errors:
            form_error.value = " ".join(non_field_errors)
            form_error.visible = True
            show_message(form_error.value, ERROR)
        else:
            show_message("Login failed. Please check your details.", ERROR)

        is_logging_in = False
        login_button.on_click = submit_login
        login_button.opacity = 1
        login_button_text.value = "Log In"
        page.update()

    async def go_register(e):
        await page.push_route("/register")

    login_button.on_click = submit_login

    card = ft.Container(
        width=470,
        bgcolor=CARD_SOFT,
        border_radius=28,
        padding=ft.Padding.symmetric(horizontal=22, vertical=26),
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Container(
                            width=46,
                            height=46,
                            bgcolor=PRIMARY_SOFT,
                            border_radius=14,
                            content=ft.Icon(ft.Icons.WAVES, color=PRIMARY, size=26),
                        ),
                        ft.Text(
                            "GrandBlue",
                            size=21,
                            weight=ft.FontWeight.BOLD,
                            color=PRIMARY_DARK,
                        ),
                    ],
                    spacing=10,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Container(height=10),
                ft.Text(
                    "Log in your account",
                    size=30,
                    weight=ft.FontWeight.BOLD,
                    color=TEXT,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "Dive back in and continue your sea adventures.",
                    size=13,
                    color=TEXT_MUTED,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=18),
                email,
                email_error,
                ft.Container(height=8),
                password,
                password_error,
                ft.Container(height=8),
                form_error,
                ft.Container(height=2),
                ft.Row(
                    controls=[
                        remember_me,
                        ft.Text("Remember me", size=13, color=TEXT_MUTED),
                    ],
                    spacing=6,
                ),
                ft.Container(height=14),
                login_button,
                ft.Container(height=6),
                ft.Container(
                    padding=10,
                    ink=True,
                    on_click=go_register,
                    content=ft.Text(
                        "Don’t have an account? Register here",
                        size=14,
                        color=LINK,
                        weight=ft.FontWeight.W_600,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ),
            ],
            spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    return ft.View(
        route="/",
        bgcolor=BG,
        controls=[
            ft.Container(
                expand=True,
                padding=ft.Padding.symmetric(horizontal=22, vertical=150),
                content=ft.Column(
                    expand=True,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(expand=1),
                        card,
                        ft.Container(expand=1),
                    ],
                ),
            )
        ],
    )