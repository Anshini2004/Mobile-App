import flet as ft


def main(page: ft.Page):
    # ── App Setup ─────────────────────
    page.title = "Main App"
    page.bgcolor = "#F7F9FC"

    # Fixed mobile-like window
    page.window.width = 550
    page.window.height = 900
    page.window.resizable = False
    page.window.maximizable = False

    page.padding = 0
    page.spacing = 0
    page.scroll = ft.ScrollMode.HIDDEN

    # ── Sea Theme ─────────────────────
    BG = "#F4FBFC"
    CARD = "#FFFFFF"
    CARD_SOFT = "#ECF8F8"
    PRIMARY = "#1D9FA5"
    PRIMARY_DARK = "#13777B"
    PRIMARY_SOFT = "#D9F3F4"
    ACCENT = "#49C5C1"
    TEXT = "#17323B"
    TEXT_MUTED = "#6D8790"
    BORDER = "#D7E8EA"
    LINK = "#148E94"

    page.bgcolor = BG

    current_page = {"name": "login"}
    main_content_ref = ft.Ref[ft.Container]()
    bottom_nav_ref = ft.Ref[ft.Container]()

    # ── Helpers ─────────────────────
    def app_logo():
        return ft.Row(
            controls=[
                ft.Container(
                    width=46,
                    height=46,
                    bgcolor=PRIMARY_SOFT,
                    border_radius=14,
                    content=ft.Icon(ft.Icons.WAVES, color=PRIMARY, size=26),
                ),
                ft.Column(
                    controls=[
                        ft.Text(
                            "GrandBlue",
                            size=21,
                            weight=ft.FontWeight.BOLD,
                            color=PRIMARY_DARK,
                        ),
                    ],
                    spacing=0,
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                ),
            ],
            spacing=10,
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def title_block(title: str, subtitle: str):
        return ft.Column(
            controls=[
                ft.Text(
                    title,
                    size=30,
                    weight=ft.FontWeight.BOLD,
                    color=TEXT,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    subtitle,
                    size=13,
                    color=TEXT_MUTED,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            spacing=6,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def input_field(label, hint="", password=False, icon=None, keyboard_type=None):
        return ft.TextField(
            label=label,
            hint_text=hint,
            password=password,
            can_reveal_password=password,
            prefix_icon=icon,
            keyboard_type=keyboard_type,
            width=420,
            height=58,
            border_color=BORDER,
            focused_border_color=PRIMARY,
            cursor_color=PRIMARY,
            filled=True,
            fill_color=CARD,
            text_size=14,
            color=TEXT,
        )

    def main_button(text, on_click):
        return ft.Container(
            width=420,
            height=54,
            bgcolor=PRIMARY,
            border_radius=18,
            ink=True,
            on_click=on_click,
            content=ft.Row(
                controls=[
                    ft.Text(
                        text,
                        color="white",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

    def text_link(text, on_click):
        return ft.Container(
            padding=10,
            ink=True,
            on_click=on_click,
            content=ft.Text(
                text,
                size=14,
                color=LINK,
                weight=ft.FontWeight.W_600,
                text_align=ft.TextAlign.CENTER,
            ),
        )

    def social_button(icon_name):
        return ft.Container(
            width=46,
            height=46,
            bgcolor=CARD,
            border_radius=14,
            border=ft.Border.all(1, BORDER),
            content=ft.Icon(icon_name, color=PRIMARY, size=22),
        )

    # ── Pages ─────────────────────
    def create_login_page():
        email = input_field(
            "Email Address",
            "Enter your email",
            icon=ft.Icons.MAIL_OUTLINE,
        )
        password = input_field(
            "Password",
            "Enter your password",
            password=True,
            icon=ft.Icons.LOCK_OUTLINE,
        )

        card = ft.Container(
            width=470,
            bgcolor=CARD_SOFT,
            border_radius=28,
            padding=ft.padding.symmetric(horizontal=22, vertical=26),
            content=ft.Column(
                controls=[
                    app_logo(),
                    ft.Container(height=10),
                    title_block(
                        "Log in your account",
                        "Dive back in and continue your sea adventures.",
                    ),
                    ft.Container(height=18),
                    email,
                    ft.Container(height=14),
                    password,
                    ft.Container(height=10),
                    ft.Container(
                        width=420,
                        content=ft.Row(
                            controls=[
                                ft.Checkbox(value=False, active_color=PRIMARY),
                                ft.Text(
                                    "Remember me",
                                    size=13,
                                    color=TEXT_MUTED,
                                ),
                            ],
                            spacing=6,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    ),
                    ft.Container(height=14),
                    main_button("Log In", lambda e: switch_page("home")),
                    ft.Container(height=6),
                    text_link(
                        "Don’t have an account? Register here",
                        lambda e: switch_page("register"),
                    ),
                ],
                spacing=0,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

        return ft.Container(
            expand=True,
            padding=ft.padding.symmetric(horizontal=22, vertical=24),
            content=ft.Column(
                controls=[
                    ft.Container(height=30),
                    card,
                ],
                scroll=ft.ScrollMode.AUTO,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

    def create_register_page():
        first_name = input_field(
            "First Name",
            "Enter first name",
            icon=ft.Icons.PERSON_OUTLINE,
        )
        last_name = input_field(
            "Last Name",
            "Enter last name",
            icon=ft.Icons.BADGE_OUTLINED,
        )
        phone_number = input_field(
            "Phone Number",
            "Enter phone number",
            icon=ft.Icons.PHONE_OUTLINED,
            keyboard_type=ft.KeyboardType.PHONE,
        )
        email = input_field(
            "Email Address",
            "Enter your email",
            icon=ft.Icons.MAIL_OUTLINE,
        )
        username = input_field(
            "Username",
            "Choose a username",
            icon=ft.Icons.ALTERNATE_EMAIL,
        )
        password = input_field(
            "Password",
            "Create a password",
            password=True,
            icon=ft.Icons.LOCK_OUTLINE,
        )
        confirm_password = input_field(
            "Confirm Password",
            "Repeat your password",
            password=True,
            icon=ft.Icons.LOCK_RESET_OUTLINED,
        )

        card = ft.Container(
            width=470,
            bgcolor=CARD_SOFT,
            border_radius=28,
            padding=ft.padding.symmetric(horizontal=22, vertical=26),
            content=ft.Column(
                controls=[
                    app_logo(),
                    ft.Container(height=10),
                    title_block(
                        "Sign Up for Free",
                        "Create your account and start exploring the sea.",
                    ),
                    ft.Container(height=18),
                    first_name,
                    ft.Container(height=12),
                    last_name,
                    ft.Container(height=12),
                    phone_number,
                    ft.Container(height=12),
                    email,
                    ft.Container(height=12),
                    username,
                    ft.Container(height=12),
                    password,
                    ft.Container(height=12),
                    confirm_password,
                    ft.Container(height=10),
                    ft.Container(
                        width=420,
                        content=ft.Row(
                            controls=[
                                ft.Checkbox(value=False, active_color=PRIMARY),
                                ft.Text(
                                    "I agree to the Terms & Conditions",
                                    size=13,
                                    color=TEXT_MUTED,
                                ),
                            ],
                            spacing=6,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    ),
                    ft.Container(height=14),
                    main_button("Create Account", lambda e: switch_page("home")),
                    ft.Container(height=18),
                    ft.Text(
                        "Or continue with",
                        size=13,
                        color=TEXT_MUTED,
                    ),
                    ft.Container(height=12),
                    ft.Row(
                        controls=[
                            social_button(ft.Icons.G_TRANSLATE),
                            social_button(ft.Icons.APPLE),
                            social_button(ft.Icons.FACEBOOK),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=14,
                    ),
                    ft.Container(height=10),
                    text_link(
                        "Already have an account? Login here",
                        lambda e: switch_page("login"),
                    ),
                ],
                spacing=0,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

        return ft.Container(
            expand=True,
            padding=ft.padding.symmetric(horizontal=22, vertical=18),
            content=ft.Column(
                controls=[card],
                scroll=ft.ScrollMode.AUTO,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

    def create_home_page():
        return ft.Container(
            expand=True,
            padding=ft.padding.only(left=22, right=22, top=26, bottom=120),
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Choose your activity",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color=TEXT,
                    ),
                    ft.Text(
                        "Home placeholder to preview the sea-themed bottom menu bar.",
                        size=13,
                        color=TEXT_MUTED,
                    ),
                    ft.Container(height=20),
                    ft.Container(
                        width=470,
                        bgcolor=PRIMARY,
                        border_radius=28,
                        padding=20,
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    "Offer of the day",
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                    color="white",
                                ),
                                ft.Text(
                                    "Best sea experience",
                                    size=13,
                                    color="#E8FFFF",
                                ),
                                ft.Container(height=18),
                                ft.Row(
                                    controls=[
                                        ft.Container(
                                            expand=True,
                                            height=120,
                                            bgcolor="#3AB8B7",
                                            border_radius=20,
                                            content=ft.Column(
                                                controls=[
                                                    ft.Icon(
                                                        ft.Icons.KAYAKING,
                                                        color="white",
                                                        size=34,
                                                    ),
                                                    ft.Text(
                                                        "Paddle Tour",
                                                        color="white",
                                                        weight=ft.FontWeight.BOLD,
                                                    ),
                                                ],
                                                alignment=ft.MainAxisAlignment.CENTER,
                                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                            ),
                                        ),
                                        ft.Container(
                                            expand=True,
                                            height=120,
                                            bgcolor="#59D4CF",
                                            border_radius=20,
                                            content=ft.Column(
                                                controls=[
                                                    ft.Icon(
                                                        ft.Icons.SCUBA_DIVING,
                                                        color="white",
                                                        size=34,
                                                    ),
                                                    ft.Text(
                                                        "Snorkeling",
                                                        color="white",
                                                        weight=ft.FontWeight.BOLD,
                                                    ),
                                                ],
                                                alignment=ft.MainAxisAlignment.CENTER,
                                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                            ),
                                        ),
                                    ],
                                    spacing=12,
                                ),
                            ],
                            spacing=0,
                        ),
                    ),
                ],
                scroll=ft.ScrollMode.AUTO,
            ),
        )

    # ── Bottom Nav ─────────────────────
    def nav_item(icon_name, label, selected, target_page):
        return ft.Container(
            expand=True,
            height=62,
            bgcolor=PRIMARY_SOFT if selected else "transparent",
            border_radius=18,
            ink=True,
            animate=ft.Animation(220, ft.AnimationCurve.EASE_OUT),
            on_click=lambda e: switch_page(target_page),
            content=ft.Column(
                controls=[
                    ft.Icon(
                        icon_name,
                        size=22,
                        color=PRIMARY if selected else TEXT_MUTED,
                    ),
                    ft.Text(
                        label,
                        size=11,
                        color=PRIMARY if selected else TEXT_MUTED,
                        weight=ft.FontWeight.W_600 if selected else ft.FontWeight.W_400,
                    ),
                ],
                spacing=2,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

    def create_bottom_nav():
        selected = current_page["name"]

        return ft.Container(
            ref=bottom_nav_ref,
            visible=False,
            left=0,
            right=0,
            bottom=0,
            margin=ft.Margin.only(left=16, right=16, bottom=16),
            padding=8,
            bgcolor=CARD,
            border_radius=26,
            border=ft.Border.all(1, BORDER),
            animate=ft.Animation(220, ft.AnimationCurve.EASE_OUT),
            content=ft.Row(
                controls=[
                    nav_item(ft.Icons.GRID_VIEW_OUTLINED, "Catalogue", selected == "home", "home"),
                    nav_item(ft.Icons.LOCAL_ACTIVITY_OUTLINED, "Activities", selected == "activities", "activities"),
                    nav_item(ft.Icons.CALENDAR_MONTH_OUTLINED, "My Bookings", selected == "bookings", "bookings"),
                    nav_item(ft.Icons.PERSON_OUTLINE, "Profile", selected == "profile", "profile"),
                ],
                spacing=8,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

    def refresh_bottom_nav():
        if bottom_nav_ref.current is None:
            return

        selected = current_page["name"]
        bottom_nav_ref.current.content = ft.Row(
            controls=[
                nav_item(ft.Icons.GRID_VIEW_OUTLINED, "Catalogue", selected == "home", "home"),
                nav_item(ft.Icons.LOCAL_ACTIVITY_OUTLINED, "Activities", selected == "activities", "activities"),
                nav_item(ft.Icons.CALENDAR_MONTH_OUTLINED, "My Bookings", selected == "bookings", "bookings"),
                nav_item(ft.Icons.PERSON_OUTLINE, "Profile", selected == "profile", "profile"),
            ],
            spacing=8,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    # ── Navigation ─────────────────────
    def switch_page(page_name: str):
        current_page["name"] = page_name

        if main_content_ref.current is None:
            return

        if page_name == "login":
            main_content_ref.current.content = create_login_page()
            if bottom_nav_ref.current:
                bottom_nav_ref.current.visible = False

        elif page_name == "register":
            main_content_ref.current.content = create_register_page()
            if bottom_nav_ref.current:
                bottom_nav_ref.current.visible = False

        elif page_name == "home":
            main_content_ref.current.content = create_home_page()
            if bottom_nav_ref.current:
                bottom_nav_ref.current.visible = True

        elif page_name == "activities":
            main_content_ref.current.content = create_home_page()
            if bottom_nav_ref.current:
                bottom_nav_ref.current.visible = True

        elif page_name == "bookings":
            main_content_ref.current.content = create_home_page()
            if bottom_nav_ref.current:
                bottom_nav_ref.current.visible = True

        elif page_name == "profile":
            main_content_ref.current.content = create_home_page()
            if bottom_nav_ref.current:
                bottom_nav_ref.current.visible = True

        else:
            main_content_ref.current.content = create_home_page()
            if bottom_nav_ref.current:
                bottom_nav_ref.current.visible = True

        refresh_bottom_nav()
        page.update()

    # ── Layout ─────────────────────
    main_content = ft.Container(
        ref=main_content_ref,
        expand=True,
        bgcolor=BG,
    )

    root = ft.Stack(
        controls=[
            main_content,
            create_bottom_nav(),
        ],
        expand=True,
    )

    page.add(root)
    switch_page("login")


if __name__ == "__main__":
    ft.run(main, assets_dir="assets")