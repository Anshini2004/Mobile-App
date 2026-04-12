import asyncio
import flet as ft

from utils.api_client import api_register, save_auth_session


def register_view(page: ft.Page):
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

    first_name = input_field("First Name", "Enter first name", icon=ft.Icons.PERSON_OUTLINE)
    first_name_error = ft.Text("", size=11, color=ERROR, visible=False)

    last_name = input_field("Last Name", "Enter last name", icon=ft.Icons.BADGE_OUTLINED)
    last_name_error = ft.Text("", size=11, color=ERROR, visible=False)

    phone_number = input_field(
        "Phone Number",
        "Enter phone number",
        icon=ft.Icons.PHONE_OUTLINED,
        keyboard_type=ft.KeyboardType.PHONE,
    )
    phone_number_error = ft.Text("", size=11, color=ERROR, visible=False)

    email = input_field(
        "Email Address",
        "Enter your email",
        icon=ft.Icons.MAIL_OUTLINE,
        keyboard_type=ft.KeyboardType.EMAIL,
    )
    email_error = ft.Text("", size=11, color=ERROR, visible=False)

    username = input_field("Username", "Choose a username", icon=ft.Icons.ALTERNATE_EMAIL)
    username_error = ft.Text("", size=11, color=ERROR, visible=False)

    password = input_field("Password", "Create a password", password=True, icon=ft.Icons.LOCK_OUTLINE)
    password_error = ft.Text("", size=11, color=ERROR, visible=False)

    confirm_password = input_field(
        "Confirm Password",
        "Repeat your password",
        password=True,
        icon=ft.Icons.LOCK_RESET_OUTLINED,
    )
    confirm_password_error = ft.Text("", size=11, color=ERROR, visible=False)

    agree_terms = ft.Checkbox(value=False, active_color=PRIMARY)
    terms_error = ft.Text("", size=12, color=ERROR, visible=False)
    form_error = ft.Text("", size=12, color=ERROR, text_align=ft.TextAlign.CENTER, visible=False)

    async def submit_register(e):
        for err in [
            first_name_error,
            last_name_error,
            phone_number_error,
            email_error,
            username_error,
            password_error,
            confirm_password_error,
        ]:
            err.value = ""
            err.visible = False

        form_error.value = ""
        form_error.visible = False
        terms_error.value = ""
        terms_error.visible = False
        page.update()

        if not agree_terms.value:
            terms_error.value = "You must agree to the Terms & Conditions."
            terms_error.visible = True
            show_message(terms_error.value, ERROR)
            page.update()
            return

        result = await asyncio.to_thread(
            api_register,
            {
                "first_name": (first_name.value or "").strip(),
                "last_name": (last_name.value or "").strip(),
                "phone_number": (phone_number.value or "").strip(),
                "email": (email.value or "").strip(),
                "username": (username.value or "").strip(),
                "password": password.value or "",
                "confirm_password": confirm_password.value or "",
            },
        )

        if result.get("fatal"):
            show_message(result["fatal"], ERROR)
            return

        if result["ok"]:
            payload = result["data"]
            save_auth_session(page, payload)
            show_message("Account created successfully!", SUCCESS)
            await page.push_route("/home")
            return

        data = result.get("data", {})

        if data.get("first_name"):
            first_name_error.value = " ".join(data["first_name"])
            first_name_error.visible = True

        if data.get("last_name"):
            last_name_error.value = " ".join(data["last_name"])
            last_name_error.visible = True

        if data.get("phone_number"):
            phone_number_error.value = " ".join(data["phone_number"])
            phone_number_error.visible = True

        if data.get("email"):
            email_error.value = " ".join(data["email"])
            email_error.visible = True

        if data.get("username"):
            username_error.value = " ".join(data["username"])
            username_error.visible = True

        if data.get("password"):
            password_error.value = " ".join(data["password"])
            password_error.visible = True

        if data.get("confirm_password"):
            confirm_password_error.value = " ".join(data["confirm_password"])
            confirm_password_error.visible = True

        non_field_errors = data.get("non_field_errors", [])
        if non_field_errors:
            form_error.value = " ".join(non_field_errors)
            form_error.visible = True
            show_message(form_error.value, ERROR)
        else:
            show_message("Registration failed. Please check your details.", ERROR)

        page.update()

    async def go_login(e):
        await page.push_route("/")

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
                    "Sign Up for Free",
                    size=30,
                    weight=ft.FontWeight.BOLD,
                    color=TEXT,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "Create your account and start exploring the sea.",
                    size=13,
                    color=TEXT_MUTED,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=18),

                first_name,
                first_name_error,
                ft.Container(height=8),

                last_name,
                last_name_error,
                ft.Container(height=8),

                phone_number,
                phone_number_error,
                ft.Container(height=8),

                email,
                email_error,
                ft.Container(height=8),

                username,
                username_error,
                ft.Container(height=8),

                password,
                password_error,
                ft.Container(height=8),

                confirm_password,
                confirm_password_error,
                ft.Container(height=10),

                ft.Row(
                    controls=[
                        agree_terms,
                        ft.Text("I agree to the Terms & Conditions", size=13, color=TEXT_MUTED),
                    ],
                    spacing=6,
                ),
                terms_error,
                ft.Container(height=8),
                form_error,
                ft.Container(height=10),

                ft.Container(
                    width=420,
                    height=54,
                    bgcolor=PRIMARY,
                    border_radius=18,
                    ink=True,
                    on_click=submit_register,
                    content=ft.Row(
                        controls=[
                            ft.Text(
                                "Create Account",
                                color="white",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                            )
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ),
                ft.Container(height=6),
                ft.Container(
                    padding=10,
                    ink=True,
                    on_click=go_login,
                    content=ft.Text(
                        "Already have an account? Log in here",
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
        route="/register",
        bgcolor=BG,
        controls=[
            ft.Container(
                expand=True,
                padding=ft.Padding.symmetric(horizontal=22, vertical=70),
                content=ft.Column(
                    expand=True,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    scroll=ft.ScrollMode.AUTO,
                    controls=[
                        card,
                    ],
                ),
            )
        ],
    )