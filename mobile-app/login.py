import flet as ft
import httpx

API_BASE_URL = "http://127.0.0.1:8000/api/"

async def login_page(page: ft.Page, go_to_profile):
    page.title = "Grand Blue – Login"
    page.window.width = 400
    page.window.height = 500

    email_tf = ft.TextField(label="Email", width=300)
    password_tf = ft.TextField(label="Password", password=True, width=300)
    message_text = ft.Text("", color="red")

    async def login_click(e):
        email = email_tf.value
        password = password_tf.value
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(f"{API_BASE_URL}login/", data={"username": email, "password": password})
            if resp.status_code == 200:
                token = resp.json().get("token")
                if token:
                    await go_to_profile(page, token)
                else:
                    message_text.value = "Token not returned"
            else:
                message_text.value = f"Login failed: {resp.text}"
        except Exception as ex:
            message_text.value = f"Login failed: {ex}"
        page.update()

    page.controls.clear()
    page.add(
        ft.Column(
            [
                ft.Text("Grand Blue – Login", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(height=20),
                email_tf,
                password_tf,
                ft.ElevatedButton("Login", on_click=login_click),
                message_text
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER
        )
    )

async def profile_page(page: ft.Page, token):
    import profile
    profile.USER_TOKEN = token
    page.controls.clear()
    await profile.main(page)  # Make sure profile.main is also async

async def main(page: ft.Page):
    await login_page(page, profile_page)

ft.app(target=main)