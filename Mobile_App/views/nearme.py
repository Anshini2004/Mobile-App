import flet as ft
import flet_map as ftm
import flet_geolocator as ftg
import httpx
import math

from utils.api_client import get_auth_headers

API_URL = "http://127.0.0.1:8000/grandblue/api/nearmeactivity/"
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
        coords = (float(data[0]["lat"]), float(data[0]["lon"]))
        GEOCODE_CACHE[location] = coords
        return coords

    return None


def nearme_view(page: ft.Page):
    geo = ftg.Geolocator()
    activity_coords = []

    marker_layer = ftm.MarkerLayer(markers=[])

    popup_container = ft.Container(
        visible=False,
        expand=True,
        alignment=ft.Alignment.CENTER,
        bgcolor=ft.Colors.with_opacity(0.45, ft.Colors.BLACK),
    )

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
                    ft.Image(src=activity["image"], height=170),
                    ft.Text(activity["name"], size=18, weight=ft.FontWeight.BOLD),
                    ft.Text(activity["description"], size=12),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.ElevatedButton("Book Now", on_click=lambda e: None),
                            ft.TextButton("Close", on_click=close_popup),
                        ],
                    ),
                ],
            ),
        )

    def show_popup(activity: dict):
        popup_container.content = build_popup(activity)
        popup_container.visible = True
        page.update()

    async def go_to_nearest():
        enabled = await geo.is_location_service_enabled()
        if not enabled:
            await geo.open_location_settings()
            return

        perm = await geo.request_permission()
        if perm not in (
            ftg.GeolocatorPermissionStatus.WHILE_IN_USE,
            ftg.GeolocatorPermissionStatus.ALWAYS,
        ):
            await geo.open_app_settings()
            return

        pos = await geo.get_last_known_position()
        if not pos:
            pos = await geo.get_current_position()

        if not pos:
            user_lat, user_lon = -20.2, 57.5
        else:
            user_lat, user_lon = pos.latitude, pos.longitude

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

        if closest:
            await map_view.move_to(
                destination=ftm.MapLatitudeLongitude(
                    closest["lat"], closest["lon"]
                ),
                zoom=15,
            )
            show_popup(closest["activity"])

    def show_near_me_dialog():
        page.show_dialog(
            ft.AlertDialog(
                title=ft.Text("Use your location?"),
                content=ft.Text("Allow GPS to find nearest activity?"),
                actions=[
                    ft.TextButton("No", on_click=lambda e: page.pop_dialog()),
                    ft.TextButton(
                        "Yes",
                        on_click=lambda e: (
                            page.pop_dialog(),
                            page.run_task(go_to_nearest)
                        ),
                    ),
                ],
            )
        )

    async def fetch_activities():
        headers = get_auth_headers(page)

        async with httpx.AsyncClient() as client:
            res = await client.get(API_URL, headers=headers)

            if res.status_code == 401:
                await page.push("/")
                return

            res.raise_for_status()
            activities = res.json()

            markers = []
            activity_coords.clear()

            grouped = {}
            for act in activities:
                grouped.setdefault(act.get("location", ""), []).append(act)

            for location, acts in grouped.items():
                coords = await geocode(client, location)
                if not coords:
                    continue

                base_lat, base_lon = coords

                for i, act in enumerate(acts):
                    angle = (i / max(len(acts), 1)) * 6.28318
                    offset = 0.0007

                    lat = base_lat + offset * math.sin(angle)
                    lon = base_lon + offset * math.cos(angle)

                    activity_coords.append({
                        "activity": act,
                        "lat": lat,
                        "lon": lon
                    })

                    def make_marker(activity=act, lat=lat, lon=lon):
                        return ftm.Marker(
                            coordinates=ftm.MapLatitudeLongitude(lat, lon),
                            content=ft.Container(
                                border_radius=12,
                                bgcolor=ft.Colors.WHITE,
                                ink=True,
                                on_click=lambda e, a=activity: show_popup(a),
                                content=ft.Image(src=activity["image"]),
                            ),
                        )

                    markers.append(make_marker())

            marker_layer.markers = markers
            page.update()

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

    near_me_btn = ft.Container(
        content=ft.FloatingActionButton(
            icon=ft.Icons.MY_LOCATION,
            on_click=lambda e: show_near_me_dialog()
        ),
        margin=ft.margin.only(bottom=100, right=10)
    )

    body = ft.Stack(
        expand=True,
        controls=[
            map_view,
            popup_container,
            ft.Container(near_me_btn, right=20, bottom=20),
        ],
    )

    page.run_task(fetch_activities)

    return body