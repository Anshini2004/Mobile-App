import flet as ft
import re
import httpx

def profile_view(page: ft.Page):

    USER_TOKEN = page.session.store.get("access_token")
    API_BASE_URL = "http://127.0.0.1:8000/api/"

    TEAL      = "#1ab4c8"
    TEAL_DARK = "#007b8f"
    CARD_BG   = "#ffffff"
    LABEL_CLR = "#7a9aaa"
    TEXT_CLR  = "#1c3340"
    HINT_CLR  = "#9bb8c4"
    RED       = "#e05252"
    GREYED    = "#cccccc"

    # ---------------- VALIDATORS ----------------
    def validate_email(v): return re.match(r'^[\w\.-]+@[A-Za-z]+\.[A-Za-z]+$', v)
    def validate_phone(v): return v.isdigit() and len(v) >= 8
    def validate_username(v): return re.match(r'^\w{3,}$', v)
    def validate_password(v): return re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', v)

    # ---------------- GET USER ----------------
   
        

    user_data = page.session.store.get("user_data") or {}

    full_name = f"{user_data.get('first_name','')} {user_data.get('last_name','')}"
    email = user_data.get('email','')

    # ---------------- AVATAR ----------------
    avatar_section = ft.Column(
        [
            ft.Container(
                content=ft.Icon(ft.Icons.PERSON, color=TEAL, size=54),
                width=90,
                height=90,
                border_radius=45,
                bgcolor="#cceef6",
                border=ft.border.all(3, TEAL),
                alignment=ft.Alignment(0, 0),
            ),
            ft.Text(full_name, size=18, weight=ft.FontWeight.BOLD, color=TEXT_CLR),
            ft.Text(email, size=12, color=HINT_CLR),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=6,
    )

    form_fields = []

    # ---------------- FIELD ----------------
    def field_row(label, value, validator=None, is_password=False):
        error = ft.Text("", color=RED, size=10)

        tf = ft.TextField(
            value=value,
            border=ft.InputBorder.NONE,
            text_style=ft.TextStyle(size=14, color=TEXT_CLR),
            password=is_password,
            disabled=True,
            expand=True
        )

        def on_change(e):
            if validator:
                error.value = "" if validator(tf.value) else f"Invalid {label.lower()}"
            page.update()

        if validator:
            tf.on_change = on_change
            form_fields.append({"label": label, "tf": tf, "validator": validator})

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(label, size=9, color=LABEL_CLR),
                    ft.Row([tf]),
                    error,
                    ft.Divider(height=1, color="#d0e8f0"),
                ]
            ),
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
        )

    password_field = field_row("PASSWORD", "", validate_password, True)

    form_card = ft.Container(
        content=ft.Column(
            [
                field_row("FIRST NAME", user_data.get("first_name",""), validate_username),
                field_row("LAST NAME", user_data.get("last_name",""), validate_username),
                field_row("USERNAME", user_data.get("username",""), validate_username),
                field_row("PHONE NUMBER", user_data.get("phone",""), validate_phone),
                field_row("EMAIL ADDRESS", user_data.get("email",""), validate_email),
                password_field,
            ]
        ),
        bgcolor=CARD_BG,
        border_radius=20,
        margin=ft.margin.symmetric(horizontal=18),
    )

    # ---------------- BUTTONS ----------------
    def enable_edit(e):
        for f in form_fields:
            f["tf"].disabled = False
        save_btn.disabled = False
        page.update()

    def save(e):
        headers = {"Authorization": f"Token {USER_TOKEN}"}

        payload = {
            f["label"].lower().replace(" ","_"): f["tf"].value
            for f in form_fields if f["label"] != "PASSWORD"
        }

        pw = next(f for f in form_fields if f["label"]=="PASSWORD")["tf"].value
        if pw: payload["password"] = pw

        try:
            httpx.patch(f"{API_BASE_URL}users/{user_data['id']}/", json=payload, headers=headers)

            dlg = ft.AlertDialog(
                title=ft.Text("Success"),
                content=ft.Text("Saved successfully"),
                actions=[ft.TextButton("OK", on_click=lambda e: page.pop_dialog())]
            )
            page.show_dialog(dlg)

        except Exception as ex:
            dlg = ft.AlertDialog(
                title=ft.Text("Error"),
                content=ft.Text(str(ex)),
                actions=[ft.TextButton("OK", on_click=lambda e: page.pop_dialog())]
            )
            page.show_dialog(dlg)

    edit_btn = ft.Container(
        content=ft.Text("Edit Profile", color="white"),
        bgcolor=TEAL,
        height=50,
        alignment=ft.Alignment(0,0),
        on_click=enable_edit
    )

    save_btn = ft.Container(
        content=ft.Text("Save Changes", color="white"),
        bgcolor=GREYED,
        height=50,
        alignment=ft.Alignment(0,0),
        disabled=True,
        on_click=save
    )

    def logout(e):
        from utils.api_client import clear_auth_session

        clear_auth_session(page)
        page.go("/login")

    logout_btn = ft.Container(
        content=ft.Text("Sign Out", color=RED),
        alignment=ft.Alignment(0,0),
        on_click=logout
    )

    # ---------------- BODY ----------------
    return ft.Column(
        [
            ft.Container(height=24),
            ft.Container(content=avatar_section, alignment=ft.Alignment(0,0)),
            ft.Container(height=20),
            form_card,
            ft.Container(height=20),
            edit_btn,
            ft.Container(height=10),
            save_btn,
            ft.Container(height=10),
            logout_btn,
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )