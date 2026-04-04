import flet as ft
import re
import httpx

# ── Replace this with the token passed from login ─────────────────────────────
USER_TOKEN = None  # default
API_BASE_URL = "http://127.0.0.1:8000/api/"  # Adjust if your API is hosted elsewhere

async def main(page: ft.Page):
    page.title = "Grand Blue – Profile"
    page.fonts = {
        "Manrope": "https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;500;600;700;800&display=swap"
    }
    page.theme = ft.Theme(font_family="Manrope")
    page.bgcolor = "#daeef8"
    page.padding = 0
    page.spacing = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 550
    page.window.height = 900

    TEAL      = "#1ab4c8"
    TEAL_DARK = "#007b8f"
    CARD_BG   = "#ffffff"
    LABEL_CLR = "#7a9aaa"
    TEXT_CLR  = "#1c3340"
    HINT_CLR  = "#9bb8c4"
    RED       = "#e05252"
    GREYED    = "#cccccc"

    # Validators
    def validate_email(value):
        pattern = r'^[\w\.-]+@[A-Za-z]+\.[A-Za-z]+$'
        return re.match(pattern, value) is not None

    def validate_phone(value):
        return value.isdigit() and len(value) >= 8

    def validate_username(value):
        pattern = r'^\w{3,}$'
        return re.match(pattern, value) is not None

    def validate_password(value):
        pattern = r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$'
        return re.match(pattern, value) is not None

    # API call to get current user
    async def get_current_user():
        headers = {"Authorization": f"Token {USER_TOKEN}"}
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{API_BASE_URL}me/", headers=headers)
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            print("Error fetching user:", e)
            return {}

    user_data = await get_current_user()

    # ── App Bar ───────────────────────────────────────────────────────────────
    app_bar = ft.Container(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.WAVES, color=TEAL, size=26),
                ft.Text(
                    "Grand Blue",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=TEAL_DARK,
                    expand=True,
                    text_align=ft.TextAlign.START,
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=CARD_BG,
        padding=ft.padding.symmetric(horizontal=20, vertical=14),
        shadow=ft.BoxShadow(blur_radius=6, color="#1a006479", offset=ft.Offset(0, 2)),
    )

    # ── Avatar ────────────────────────────────────────────────────────────────
    full_name = f"{user_data.get('first_name','')} {user_data.get('last_name','')}"
    email = user_data.get('email','')
    avatar_section = ft.Column(
        [
            ft.Container(
                content=ft.Icon(ft.Icons.PERSON, color=TEAL, size=54),
                width=90,
                height=90,
                border_radius=45,
                bgcolor="#cceef6",
                border=ft.border.all(3, TEAL),
                alignment=ft.Alignment.CENTER,
            ),
            ft.Text(full_name, size=18, weight=ft.FontWeight.BOLD, color=TEXT_CLR),
            ft.Text(email, size=12, color=HINT_CLR, weight=ft.FontWeight.W_500),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=6,
    )

    # ── Field helper ──────────────────────────────────────────────────────────
    form_fields = []

    def field_row(label, value, icon=None, is_password=False, validator=None):
        error_text = ft.Text("", color=RED, size=10)
        tf = ft.TextField(
            value=value,
            border=ft.InputBorder.NONE,
            content_padding=ft.padding.symmetric(horizontal=0, vertical=4),
            text_style=ft.TextStyle(size=14, weight=ft.FontWeight.W_500, color=TEXT_CLR),
            cursor_color=TEAL,
            expand=True,
            password=is_password,
            disabled=True
        )
        visibility_icon = ft.Icon(ft.Icons.VISIBILITY, color="#89b2bc", size=20)

        def toggle_password(e):
            tf.password = not tf.password
            visibility_icon.icon = ft.Icons.VISIBILITY if tf.password else ft.Icons.VISIBILITY_OFF
            page.update()

        def on_change(e):
            if validator:
                # Password is optional: only validate if non-empty
                if is_password and tf.value.strip() == "":
                    error_text.value = ""
                else:
                    error_text.value = "" if validator(tf.value) else f"Invalid {label.lower()}"

            # Enable save only if all non-disabled fields are valid
            save_btn.disabled = any(
                f["tf"].disabled == False and (
                    # Password empty is ok
                    (f["tf"] == password_field.content.controls[1].controls[0] and f["tf"].value.strip() != "" and not f["validator"](f["tf"].value)) 
                    or (f["tf"] != password_field.content.controls[1].controls[0] and not f["validator"](f["tf"].value))
                )
                for f in form_fields if "validator" in f
            )
            update_button_styles()
            page.update()

        if validator:
            tf.on_change = on_change
            form_fields.append({
                "label": label,
                "tf": tf,
                "validator": validator
            })

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(label, size=9, weight=ft.FontWeight.BOLD, color=LABEL_CLR),
                    ft.Row(
                        [
                            tf,
                            *([ft.Container(content=visibility_icon, on_click=toggle_password)] if is_password else []),
                            *([ft.Icon(icon, color=HINT_CLR, size=18)] if icon and not is_password else []),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    error_text,
                    ft.Divider(height=1, color="#d0e8f0"),
                ],
                spacing=0,
            ),
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
        )

    # ── Form card ─────────────────────────────────────────────────────────────
    password_field = field_row("PASSWORD", "", is_password=True, validator=validate_password)
    password_field.content.controls[1].controls[0].disabled = True  # hide initially

    form_card = ft.Container(
        content=ft.Column(
            [
                field_row("FIRST NAME", user_data.get('first_name',''), ft.Icons.PERSON_OUTLINE, validator=validate_username),
                field_row("LAST NAME", user_data.get('last_name',''), ft.Icons.BADGE_OUTLINED, validator=validate_username),
                field_row("USERNAME", user_data.get('username',''), ft.Icons.ALTERNATE_EMAIL, validator=validate_username),
                field_row("PHONE NUMBER", user_data.get('phone',''), ft.Icons.PHONE_OUTLINED, validator=validate_phone),
                field_row("EMAIL ADDRESS", user_data.get('email',''), ft.Icons.MAIL_OUTLINE, validator=validate_email),
                password_field,
            ],
            spacing=0,
        ),
        bgcolor=CARD_BG,
        border_radius=20,
        margin=ft.margin.symmetric(horizontal=18),
        shadow=ft.BoxShadow(blur_radius=14, color="#18006479", offset=ft.Offset(0, 4)),
    )

    # ── Buttons ───────────────────────────────────────────────────────────────
    def update_button_styles():
        if save_btn.disabled:
            save_btn.gradient = None
            save_btn.bgcolor = GREYED
        else:
            save_btn.gradient = ft.LinearGradient(begin=ft.Alignment(-1,0), end=ft.Alignment(1,0), colors=[TEAL, TEAL_DARK])
            save_btn.bgcolor = None
        if edit_btn.disabled:
            edit_btn.gradient = None
            edit_btn.bgcolor = GREYED
        else:
            edit_btn.gradient = ft.LinearGradient(begin=ft.Alignment(-1,0), end=ft.Alignment(1,0), colors=[TEAL, TEAL_DARK])
            edit_btn.bgcolor = None
        page.update()

    async def save_changes(e):
        headers = {"Authorization": f"Token {USER_TOKEN}"}
        def get_field(label):
            return next(f for f in form_fields if f["label"] == label)["tf"].value.strip()

        payload = {
            "first_name": get_field("FIRST NAME"),
            "last_name": get_field("LAST NAME"),
            "username": get_field("USERNAME"),
            "phone": get_field("PHONE NUMBER"),
            "email": get_field("EMAIL ADDRESS"),
        }

        password_value = get_field("PASSWORD")
        if password_value:
            payload["password"] = password_value
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.patch(f"{API_BASE_URL}users/{user_data['id']}/", json=payload, headers=headers)
                resp.raise_for_status()
                for f in form_fields:
                    f["tf"].disabled = True
                save_btn.disabled = True
                edit_btn.disabled = False
                update_button_styles()
        except httpx.HTTPStatusError as ex:
            print("STATUS:", ex.response.status_code)
            print("RESPONSE TEXT:", ex.response.text)
            try:
                print("JSON ERROR:", ex.response.json())
            except:
                print("No JSON response")

    save_btn = ft.Container(
        content=ft.Row(
            [ft.Icon(ft.Icons.SAVE_OUTLINED, color="white", size=18),
             ft.Text("Save Changes", color="white", size=15, weight=ft.FontWeight.BOLD)],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
        ),
        gradient=None,
        bgcolor=GREYED,
        border_radius=30,
        height=50,
        margin=ft.margin.symmetric(horizontal=18),
        ink=True,
        disabled=True,
        on_click=save_changes,
    )

    async def edit_profile(e):
        current_pw_input = ft.TextField(password=True, label="Current Password", autofocus=True)
        msg_text = ft.Text("", color=RED)

        async def verify_password(ev):
            try:
                async with httpx.AsyncClient() as client:
                    resp = await client.post(
                        f"{API_BASE_URL}login/",
                        data={"username": user_data.get("email"), "password": current_pw_input.value}
                    )
                if resp.status_code == 200 and resp.json().get("token"):
                    # Enable fields, disable edit
                    for f in form_fields:
                        f["tf"].disabled = False
                    save_btn.disabled = False
                    edit_btn.disabled = True
                    password_field.content.controls[1].controls[0].disabled = False
                    page.pop_dialog()
                    update_button_styles()
                else:
                    msg_text.value = "Incorrect password"
                    page.update()
            except Exception as ex:
                msg_text.value = f"Error: {ex}"
                page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Enter Current Password"),
            content=ft.Container(content=ft.Column([current_pw_input, msg_text], spacing=5), width=250, height=50),
            actions=[ft.TextButton("Cancel", on_click=lambda e: page.pop_dialog()),
                     ft.Button("Verify", on_click=verify_password)],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        page.show_dialog(dlg)

    edit_btn = ft.Container(
        content=ft.Row(
            [ft.Icon(ft.Icons.EDIT, color="white", size=18),
             ft.Text("Edit Profile", color="white", size=15, weight=ft.FontWeight.BOLD)],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
        ),
        gradient=ft.LinearGradient(begin=ft.Alignment(-1,0), end=ft.Alignment(1,0), colors=[TEAL, TEAL_DARK]),
        border_radius=30,
        height=50,
        margin=ft.margin.symmetric(horizontal=18),
        ink=True,
        disabled=False,
        on_click=edit_profile,
    )

    # ── Sign Out ──────────────────────────────────────────────────────────────
    async def sign_out(e):
        global USER_TOKEN
        USER_TOKEN = None
        page.clean()
        page.update()

    sign_out_btn = ft.Container(
        content=ft.Row(
            [ft.Icon(ft.Icons.LOGOUT, color=RED, size=16),
             ft.Text("Sign Out", color=RED, size=13, weight=ft.FontWeight.W_600)],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=6,
        ),
        on_click=sign_out,
        ink=True,
        border_radius=8,
        padding=ft.padding.symmetric(vertical=6),
    )

    # ── Bottom nav ───────────────────────────────────────────────────────────
    def nav_item(icon, label, active=False):
        color = "white" if active else LABEL_CLR
        bg = TEAL if active else ft.Colors.TRANSPARENT
        return ft.Container(
            content=ft.Column(
                [ft.Icon(icon, color=color, size=22),
                 ft.Text(label, size=10, color=color, weight=ft.FontWeight.BOLD)],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=3,
            ),
            bgcolor=bg,
            border_radius=14,
            padding=ft.padding.symmetric(horizontal=16, vertical=8),
        )

    bottom_nav = ft.Container(
        content=ft.Row(
            [nav_item(ft.Icons.HOME_OUTLINED, "Home"),
             nav_item(ft.Icons.DIRECTIONS_BOAT, "Bookings"),
             nav_item(ft.Icons.PERSON, "Profile", active=True)],
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
        ),
        bgcolor=CARD_BG,
        padding=ft.padding.symmetric(vertical=10, horizontal=10),
        shadow=ft.BoxShadow(blur_radius=10, color="#22000000", offset=ft.Offset(0, -2)),
    )

    # ── Body ──────────────────────────────────────────────────────────────────
    body = ft.Column(
        [ft.Container(height=24),
         ft.Container(content=avatar_section, alignment=ft.Alignment.CENTER),
         ft.Container(height=20),
         form_card,
         ft.Container(height=20),
         edit_btn,
         ft.Container(height=10),
         save_btn,
         ft.Container(height=10),
         sign_out_btn,
         ft.Container(height=20)],
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        spacing=0,
    )

    page.add(ft.Column([app_bar, body, bottom_nav], spacing=0, expand=True))