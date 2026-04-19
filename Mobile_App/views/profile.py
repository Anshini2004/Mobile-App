import asyncio
import re
import flet as ft
import httpx

from utils.api_client import get_auth_headers, api_logout

API_BASE_URL = "http://127.0.0.1:8000/api"


def profile_view(page: ft.Page):

    TEAL = "#1ab4c8"
    CARD_BG = "#ffffff"
    RED = "#e05252"
    GREYED = "#cccccc"

    def validate_email(v): return re.match(r'^[\w\.-]+@[A-Za-z]+\.[A-Za-z]+$', v or "") is not None
    def validate_phone(v): return (v or "").isdigit() and len(v or "") >= 8
    def validate_username(v): return re.match(r'^\w{3,}$', v or "") is not None
    def validate_password(v): return v == "" or re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', v or "") is not None

    user_data = page.session.store.get("user_data") or {}

    avatar = ft.Column(
        [
            ft.Container(
                content=ft.Icon(ft.Icons.PERSON, color=TEAL, size=54),
                width=90, height=90, border_radius=45,
                bgcolor="#cceef6",
                border=ft.border.all(3, TEAL),
                alignment=ft.Alignment.CENTER,
            ),
            ft.Text(
                f"{user_data.get('first_name','')} {user_data.get('last_name','')}",
                size=18, weight=ft.FontWeight.BOLD, color="#FFFFFF"
            ),
            ft.Text(user_data.get("email", ""), size=12, color="#ffffff"),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=6,
    )

    form_fields = []

    def field(label, value, validator=None, password=False):
        err = ft.Text("", color=RED, size=10)

        tf = ft.TextField(
            value=value,
            border=ft.InputBorder.NONE,
            password=password,
            can_reveal_password=password,
            disabled=True,
            expand=True,
            color="#000000"
        )

        def on_change(e):
            if validator:
                err.value = "" if validator(tf.value) else f"Invalid {label.lower()}"

            save_btn.disabled = any(
                f["validator"] and not f["validator"](f["tf"].value)
                for f in form_fields if not f["tf"].disabled
            )

            update_btns()
            page.update()

        if validator:
            tf.on_change = on_change
            form_fields.append({"label": label, "tf": tf, "validator": validator})

        return ft.Container(
            content=ft.Column([
                ft.Text(label, size=10, color="#000000"),
                ft.Row([tf]),
                err,
                ft.Divider(height=1),
            ]),
            padding=10
        )

    password_field = field("PASSWORD", "", validate_password, True)

    form = ft.Container(
        content=ft.Column([
            field("FIRST NAME", user_data.get("first_name",""), validate_username),
            field("LAST NAME", user_data.get("last_name",""), validate_username),
            field("USERNAME", user_data.get("username",""), validate_username),
            field("PHONE", user_data.get("phone",""), validate_phone),
            field("EMAIL", user_data.get("email",""), validate_email),
            password_field,
        ]),
        bgcolor=CARD_BG,
        border_radius=20,
        margin=18,
    )

    def update_btns():
        save_btn.bgcolor = GREYED if save_btn.disabled else TEAL
        edit_btn.bgcolor = GREYED if edit_btn.disabled else TEAL
        page.update()

    async def save_async():
        headers = get_auth_headers(page)

        payload = {
            f["label"].lower().replace(" ", "_"): f["tf"].value
            for f in form_fields if f["label"] != "PASSWORD"
        }

        pw = next(f for f in form_fields if f["label"] == "PASSWORD")["tf"].value
        if pw:
            payload["password"] = pw

        async with httpx.AsyncClient() as client:
            resp = await client.patch(
                f"{API_BASE_URL}/auth/me/",
                json=payload,
                headers=headers
            )

        if resp.status_code == 401:
            page.go("/")
            return

        if resp.status_code == 200:
            page.session.store.set("user_data", resp.json())

            page.snack_bar = ft.SnackBar(ft.Text("Saved"), bgcolor=TEAL)
            page.snack_bar.open = True

            for f in form_fields:
                f["tf"].disabled = True

            save_btn.disabled = True
            edit_btn.disabled = False
            update_btns()
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Error saving"), bgcolor=RED)
            page.snack_bar.open = True

        page.update()

    def save(e):
        page.run_task(save_async)

    def edit(e):
        for f in form_fields:
            f["tf"].disabled = False
        save_btn.disabled = False
        edit_btn.disabled = True
        update_btns()

    async def logout_async():
        await asyncio.to_thread(api_logout, page)
        page.go("/login")

    def logout(e):
        page.run_task(logout_async)

    save_btn = ft.Container(
        content=ft.Text("Save", color="white"),
        height=50,
        bgcolor=GREYED,
        border_radius=20,
        alignment=ft.Alignment.CENTER,
        disabled=True,
        on_click=save,
    )

    edit_btn = ft.Container(
        content=ft.Text("Edit", color="white"),
        height=50,
        bgcolor=TEAL,
        border_radius=20,
        alignment=ft.Alignment.CENTER,
        on_click=edit,
    )

    logout_btn = ft.Container(
        content=ft.Text("Logout", color=RED),
        on_click=logout,
        alignment=ft.Alignment.CENTER,
        padding=10,
    )

    body = ft.Column([
        ft.Container(height=20),
        ft.Container(content=avatar, alignment=ft.Alignment.CENTER),
        ft.Container(height=20),
        form,
        edit_btn,
        save_btn,
        logout_btn,
    ], scroll=ft.ScrollMode.AUTO)

    return body