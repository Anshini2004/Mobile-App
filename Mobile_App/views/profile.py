import asyncio
import re
import flet as ft
import httpx

from utils.api_client import get_auth_headers, api_logout

API_BASE_URL = "http://127.0.0.1:8000/grandblue/api"


async def profile_view(page: ft.Page):
    page.title = "Grand Blue – Profile"
    page.bgcolor = "#daeef8"
    page.padding = 0
    page.spacing = 0
    page.window.width = 550
    page.window.height = 900

    TEAL = "#1ab4c8"
    TEAL_DARK = "#007b8f"
    CARD_BG = "#ffffff"
    LABEL_CLR = "#7a9aaa"
    TEXT_CLR = "#1c3340"
    HINT_CLR = "#9bb8c4"
    RED = "#e05252"
    GREYED = "#cccccc"

    # ── Validators ─────────────────────────────────────────────
    def validate_email(v): return re.match(r'^[\w\.-]+@[A-Za-z]+\.[A-Za-z]+$', v or "") is not None
    def validate_phone(v): return (v or "").isdigit() and len(v or "") >= 8
    def validate_username(v): return re.match(r'^\w{3,}$', v or "") is not None
    def validate_password(v): return v == "" or re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', v or "") is not None

    # ── Load user from session ─────────────────────────────────
    user_data = page.session.store.get("user_data") or {}

    # ── Avatar ────────────────────────────────────────────────
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
                size=18, weight=ft.FontWeight.BOLD, color=TEXT_CLR
            ),
            ft.Text(user_data.get("email", ""), size=12, color=HINT_CLR),
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
            disabled=True,
            expand=True,
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
                ft.Text(label, size=9, color=LABEL_CLR),
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

    async def save(e):
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

    async def edit(e):
        for f in form_fields:
            f["tf"].disabled = False
        save_btn.disabled = False
        edit_btn.disabled = True
        update_btns()

    async def logout(e):
        await asyncio.to_thread(api_logout, page)
        page.go("/")

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
        avatar,
        ft.Container(height=20),
        form,
        edit_btn,
        save_btn,
        logout_btn,
    ], scroll=ft.ScrollMode.AUTO)

    return ft.View(
        "/profile",
        controls=[body]
    )