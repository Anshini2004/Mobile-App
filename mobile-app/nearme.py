#to test this without logging in, remove isauthenticated line from ActivityViewSet in merger/api/viewsets.py, then in this file, remove the content of headers, search, "headers = {"
import flet as ft
import flet_map as ftm
import flet_geolocator as ftg 
import httpx
import math

API_URL = "http://127.0.0.1:8000/api/activities/"
TOKEN = "YOUR_TOKEN_HERE"

GEOCODE_CACHE = {}


async def geocode(client: httpx.AsyncClient, location: str):
    if location in GEOCODE_CACHE:
        return GEOCODE_CACHE[location]

    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": f"{location}, Mauritius",
        "format": "json",
        "limit": 1,
    }

    r = await client.get(
        url,
        params=params,
        headers={"User-Agent": "flet-app"}
    )

    data = r.json()
    if data:
        coords = (
            float(data[0]["lat"]),
            float(data[0]["lon"])
        )
        GEOCODE_CACHE[location] = coords
        return coords

    return None


async def main(page: ft.Page):
    page.title = "Activity Map"
    page.padding = 0
    page.spacing = 0

    # ─────────────────────────────
    # GEOLOCATOR (GPS)
    # ─────────────────────────────
    geo = ftg.Geolocator()
    

    # store all activity coordinates for "near me"
    activity_coords = []

    # ─────────────────────────────
    # MAP LAYER
    # ─────────────────────────────
    marker_layer = ftm.MarkerLayer(markers=[])

    # ─────────────────────────────
    # POPUP STATE (overlay)
    # ─────────────────────────────
    popup_container = ft.Container(
        visible=False,
        expand=True,
        alignment=ft.Alignment.CENTER,
        bgcolor=ft.Colors.with_opacity(0.45, ft.Colors.BLACK),
    )

    popup_content_holder = ft.Container()

    def close_popup(e=None):
        popup_container.visible = False
        popup_container.content = None
        page.update()

    def build_popup(activity: dict):
        return ft.Container(
            height=350,
            width=340,
            padding=16,
            border_radius=18,
            bgcolor=ft.Colors.WHITE,
            shadow=ft.BoxShadow(blur_radius=25),
            content=ft.Column(
                spacing=10,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Image(
                        src=activity["image"],
                        height=170,
                        fit=ft.BoxFit.CONTAIN,
                    ),
                    ft.Text(
                        activity["name"],
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                        color = ft.Colors.BLACK
                    ),
                    ft.Text(
                        activity["description"],
                        size=12,
                        text_align=ft.TextAlign.CENTER,
                        color = ft.Colors.BLACK
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.ElevatedButton(
                                "Book Now",
                                on_click=lambda e: None,
                                color = ft.Colors.WHITE
                            ),
                            ft.TextButton(
                                "Close",
                                on_click=close_popup
                            ),
                        ],
                    ),
                ],
            ),
        )

    def show_popup(activity: dict):
        popup_container.content = build_popup(activity)
        popup_container.visible = True
        page.update()

    # ─────────────────────────────
    # NEAR ME LOGIC
    # ─────────────────────────────
    async def go_to_nearest():
        # 1. Check if location service is ON
        enabled = await geo.is_location_service_enabled()
        if not enabled:
            print("Location service is OFF")
            await geo.open_location_settings()
            return

        # 2. Request permission
        perm = await geo.request_permission()

        if perm not in (
            ftg.GeolocatorPermissionStatus.WHILE_IN_USE,
            ftg.GeolocatorPermissionStatus.ALWAYS,
        ):
            print("Permission denied:", perm)
            await geo.open_app_settings()
            return

        # 3. Try last known position (fast)
        pos = await geo.get_last_known_position()

        # 4. Fallback to current position (slow but accurate)
        if not pos:
            pos = await geo.get_current_position()

        # 5. HARD fallback (IMPORTANT)
        if not pos:
            print("GPS failed → using default Mauritius location")
            user_lat, user_lon = -20.2, 57.5  # Mauritius fallback
        else:
            user_lat, user_lon = pos.latitude, pos.longitude

        # 6. Find closest activity
        closest = None
        min_dist = float("inf")

        for item in activity_coords:
            d = await geo.distance_between(
                user_lat,
                user_lon,
                item["lat"],
                item["lon"],
            )

            if d < min_dist:
                min_dist = d
                closest = item

        # 7. Move map + show popup
        if closest:
            await map_view.move_to(
                destination=ftm.MapLatitudeLongitude(
                    closest["lat"],
                    closest["lon"],
                ),
                zoom=15,
            )

            show_popup(closest["activity"])
        else:
            print("No activities found")

    def show_near_me_dialog():
        dialog = ft.AlertDialog(
            title=ft.Text("Use your location?"),
            content=ft.Text("Allow GPS to find nearest activity?"),
            actions=[
                ft.TextButton(
                    "No",
                    on_click=lambda e: page.pop_dialog()
                ),
                ft.TextButton(
                    "Yes",
                    on_click=lambda e: (
                        page.pop_dialog(),
                        page.run_task(go_to_nearest)
                    )
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        page.show_dialog(dialog)

    # ─────────────────────────────
    # FETCH ACTIVITIES
    # ─────────────────────────────
    async def fetch_activities():
        headers = {"Authorization": f"Token {TOKEN}"}  # remove the inside to test without authentication. headers = {"Authorization": f"Token {TOKEN}"}

        async with httpx.AsyncClient() as client:
            res = await client.get(API_URL, headers=headers)
            res.raise_for_status()

            activities = res.json()

            markers = []
            activity_coords.clear()

            # ─────────────────────────────
            # GROUP BY LOCATION
            # ─────────────────────────────
            grouped = {}

            for act in activities:
                loc = act.get("location", "")
                grouped.setdefault(loc, []).append(act)

            # ─────────────────────────────
            # BUILD MARKERS WITH OFFSET
            # ─────────────────────────────
            for location, acts in grouped.items():

                coords = await geocode(client, location)
                if not coords:
                    continue

                base_lat, base_lon = coords

                for i, act in enumerate(acts):
                    if not isinstance(act, dict):
                        continue

                    # ─────────────────────────────
                    # SPREAD IN SMALL CIRCLE
                    # ─────────────────────────────
                    angle = (i / max(len(acts), 1)) * 6.28318
                    offset = 0.0007

                    lat = base_lat + offset * math.sin(angle)
                    lon = base_lon + offset * math.cos(angle)

                    # store for GPS nearest calculation
                    activity_coords.append({
                        "activity": act,
                        "lat": lat,
                        "lon": lon
                    })

                    def make_marker(activity=act, lat=lat, lon=lon):

                        def on_click(e, a=activity):
                            show_popup(a)

                        return ftm.Marker(
                            coordinates=ftm.MapLatitudeLongitude(lat, lon),
                            content=ft.Container(
                                border_radius=12,
                                bgcolor=ft.Colors.WHITE,
                                shadow=ft.BoxShadow(blur_radius=10),
                                ink=True,
                                on_click=on_click,
                                content=ft.Image(src=activity["image"]),
                            ),
                        )

                    markers.append(make_marker())

            marker_layer.markers = markers
            page.update()

    # ─────────────────────────────
    # MAP VIEW
    # ─────────────────────────────
    map_view = ftm.Map(
        expand=True,
        initial_center=ftm.MapLatitudeLongitude(-20.2, 57.5),
        initial_zoom=10,
        layers=[
            ftm.TileLayer(
                url_template="https://tile.memomaps.de/tilegen/{z}/{x}/{y}.png"
            ),
            marker_layer,
        ],
    )

    # ─────────────────────────────
    # NEAR ME BUTTON
    # ─────────────────────────────
    near_me_btn = ft.FloatingActionButton(
        icon=ft.Icons.MY_LOCATION,
        on_click=lambda e: show_near_me_dialog()
    )

    # ─────────────────────────────
    # UI STACK (MAP + POPUP + BUTTON)
    # ─────────────────────────────
    page.add(
        ft.Stack(
            expand=True,
            controls=[
                map_view,
                popup_container,

                # floating "near me" button
                ft.Container(
                    near_me_btn,
                    right=20,
                    bottom=20,
                ),
            ],
        )
    )

    await fetch_activities()


ft.run(main)