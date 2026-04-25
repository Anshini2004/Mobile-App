import flet as ft
import flet_map as ftm
import calendar
import requests
from datetime import datetime, date
from urllib.parse import quote_plus
from utils.config import IMAGE_BASE_URL

BASE_URL = "http://127.0.0.1:8000/grandblue"


def fix_image_url(url):
    if not url:
        return None

    url = str(url)

    if url.startswith("http://127.0.0.1:8000"):
        return url.replace("http://127.0.0.1:8000", IMAGE_BASE_URL)

    if url.startswith("http://localhost:8000"):
        return url.replace("http://localhost:8000", IMAGE_BASE_URL)

    if url.startswith("http://") or url.startswith("https://"):
        return url

    if url.startswith("/"):
        return f"{IMAGE_BASE_URL}{url}"

    return f"{IMAGE_BASE_URL}/{url}"


def activity_detail_view(page: ft.Page, activity_id: int):
    PRIMARY = "#0A2540"
    TEAL = "#2CBFB1"
    BG = "#F5F7FA"
    CARD = "#FFFFFF"
    TEXT = "#111827"
    MUTED = "#6B7280"
    BORDER = "#E5E7EB"
    LIGHT = "#F9FAFB"
    AMBER = "#F59E0B"
    ORANGE = "#F97316"
    ERROR = "#DC2626"
    HERO_FALLBACK = "#092846"

    # Unavailable-date colours
    UNAVAILABLE_BG = "#FDECEC"
    UNAVAILABLE_BORDER = "#F4B7B7"
    UNAVAILABLE_TEXT = "#C96C6C"

    activity_data = {"data": None}
    selected_image = {"index": 0}
    description_expanded = {"value": False}
    booking_offset = {"value": 900.0}
    scroll_pixels = {"value": 0.0}
    hero_drag_dx = {"value": 0.0}

    # Persist expansion state across rebuilds
    expanded_sections = {
        "rules": False,
        "safety": False,
        "cancellation": False,
        "reviews": False,
    }

    today = date.today()
    current = {"year": today.year, "month": today.month}
    sel = {"date": None}
    tickets = {"count": 1}

    month_label = ft.Text("", size=15, weight=ft.FontWeight.BOLD, color=TEXT)
    calendar_grid = ft.Column(spacing=8)
    ticket_text = ft.Text("1", size=16, weight=ft.FontWeight.BOLD, color=TEXT)
    book_btn_text = ft.Text("Book Now", color="white", size=16, weight=ft.FontWeight.W_600)

    summary_date_value = ft.Text("Select a date", size=13, color=TEXT, weight=ft.FontWeight.W_600)
    summary_guest_value = ft.Text("1 guest", size=13, color=TEXT, weight=ft.FontWeight.W_600)
    summary_total_value = ft.Text("Rs 0", size=20, color=TEXT, weight=ft.FontWeight.BOLD)

    scroll_col = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        spacing=0,
        expand=True,
    )

    scroll_col.controls = [
        ft.Container(
            height=700,
            alignment=ft.Alignment(0, 0),
            content=ft.Column(
                controls=[
                    ft.ProgressRing(color=TEAL),
                    ft.Text("Loading activity…", color=MUTED, size=13),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=14,
            ),
        )
    ]

    def soft_card(content, padding=20, margin=None):
        return ft.Container(
            bgcolor=CARD,
            border_radius=20,
            border=ft.Border.all(1, BORDER),
            padding=padding,
            margin=margin,
            shadow=ft.BoxShadow(
                blur_radius=20,
                spread_radius=0,
                color="#14000000",
                offset=ft.Offset(0, 8),
            ),
            content=content,
        )

    def section_title(text: str, subtitle=None):
        controls = [
            ft.Text(text, size=18, weight=ft.FontWeight.BOLD, color=TEXT),
        ]
        if subtitle:
            controls.append(ft.Text(subtitle, size=12, color=MUTED))
        return ft.Column(controls, spacing=4)

    def info_chip(icon, label, accent=False):
        return ft.Container(
            border_radius=18,
            bgcolor="#EAF7F5" if accent else LIGHT,
            padding=ft.padding.symmetric(horizontal=12, vertical=9),
            content=ft.Row(
                spacing=7,
                controls=[
                    ft.Icon(icon, size=15, color=TEAL if accent else MUTED),
                    ft.Text(label, size=12, color=TEXT, weight=ft.FontWeight.W_600),
                ],
            ),
        )

    def metric_card(icon, title, value):
        return ft.Container(
            expand=True,
            border_radius=18,
            bgcolor=LIGHT,
            padding=ft.padding.symmetric(horizontal=14, vertical=14),
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Container(
                        width=36,
                        height=36,
                        border_radius=18,
                        bgcolor="#EAF7F5",
                        alignment=ft.Alignment(0, 0),
                        content=ft.Icon(icon, size=18, color=TEAL),
                    ),
                    ft.Text(title, size=11, color=MUTED),
                    ft.Text(value, size=13, color=TEXT, weight=ft.FontWeight.BOLD),
                ],
            ),
        )

    def star_row(avg: float) -> ft.Row:
        avg = avg or 0.0
        full = int(avg)
        half = 1 if (avg - full) >= 0.5 else 0
        empty = 5 - full - half
        return ft.Row(
            controls=[
                *[ft.Icon(ft.Icons.STAR, color=AMBER, size=15) for _ in range(full)],
                *[ft.Icon(ft.Icons.STAR_HALF, color=AMBER, size=15) for _ in range(half)],
                *[ft.Icon(ft.Icons.STAR_BORDER, color=AMBER, size=15) for _ in range(empty)],
            ],
            spacing=1,
        )

    def handle_expansion_change(section_key: str):
        def _handler(e):
            expanded_sections[section_key] = str(e.data).lower() == "true"
            page.update()
        return _handler

    def bullet_section(title, items, icon, icon_color, subtitle=None, section_key=""):
        if not items:
            return ft.Container(height=0)

        return soft_card(
            ft.ExpansionTile(
                expanded=expanded_sections.get(section_key, False),
                maintain_state=True,
                on_change=handle_expansion_change(section_key),
                tile_padding=ft.padding.all(0),
                controls_padding=ft.padding.only(top=8, bottom=0, left=0, right=0),
                icon_color=MUTED,
                collapsed_icon_color=MUTED,
                text_color=TEXT,
                collapsed_text_color=TEXT,
                shape=ft.RoundedRectangleBorder(
                    radius=16,
                    side=ft.BorderSide.none(),
                ),
                collapsed_shape=ft.RoundedRectangleBorder(
                    radius=16,
                    side=ft.BorderSide.none(),
                ),
                leading=ft.Container(
                    width=34,
                    height=34,
                    border_radius=17,
                    bgcolor=LIGHT,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Icon(icon, size=16, color=icon_color),
                ),
                title=ft.Text(
                    title,
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=TEXT,
                ),
                subtitle=ft.Text(
                    subtitle or "Tap to view details",
                    size=12,
                    color=MUTED,
                ),
                controls=[
                    ft.Column(
                        spacing=10,
                        controls=[
                            ft.Row(
                                spacing=12,
                                vertical_alignment=ft.CrossAxisAlignment.START,
                                controls=[
                                    ft.Container(
                                        width=24,
                                        height=24,
                                        border_radius=12,
                                        bgcolor="#EEF2F7",
                                        alignment=ft.Alignment(0, 0),
                                        content=ft.Icon(
                                            ft.Icons.CHECK,
                                            size=13,
                                            color=icon_color,
                                        ),
                                    ),
                                    ft.Text(
                                        item,
                                        size=13,
                                        color=MUTED,
                                        expand=True,
                                    ),
                                ],
                            )
                            for item in items
                        ],
                    )
                ],
            ),
            padding=16,
        )

    def review_card(r: dict) -> ft.Container:
        rating = int(r.get("rating", 5) or 5)
        raw_dt = r.get("created_at", "")
        try:
            dt_label = datetime.fromisoformat(raw_dt).strftime("%d %b %Y")
        except Exception:
            dt_label = str(raw_dt)[:10]

        return soft_card(
            ft.Column(
                spacing=12,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(
                                spacing=10,
                                controls=[
                                    ft.Container(
                                        width=42,
                                        height=42,
                                        border_radius=21,
                                        bgcolor="#EAF7F5",
                                        alignment=ft.Alignment(0, 0),
                                        content=ft.Icon(ft.Icons.PERSON, size=22, color=TEAL),
                                    ),
                                    ft.Column(
                                        spacing=2,
                                        controls=[
                                            ft.Text(
                                                r.get("author", "Guest"),
                                                size=13,
                                                weight=ft.FontWeight.W_600,
                                                color=TEXT,
                                            ),
                                            ft.Text(dt_label, size=11, color=MUTED),
                                        ],
                                    ),
                                ],
                            ),
                            ft.Container(
                                border_radius=16,
                                bgcolor=LIGHT,
                                padding=ft.padding.symmetric(horizontal=10, vertical=6),
                                content=ft.Row(
                                    spacing=2,
                                    controls=[
                                        ft.Icon(ft.Icons.STAR, size=12, color=AMBER)
                                        for _ in range(rating)
                                    ],
                                ),
                            ),
                        ],
                    ),
                    ft.Text(
                        r.get("comment", ""),
                        size=13,
                        color=MUTED,
                        selectable=True,
                    ),
                ],
            )
        )

    def refresh_book_btn():
        d = activity_data["data"]
        if d and d.get("base_price") is not None:
            total = float(d["base_price"]) * tickets["count"]
            book_btn_text.value = f"Book for Rs {total:,.0f}"

    def refresh_booking_summary():
        d = activity_data["data"]
        summary_date_value.value = (
            sel["date"].strftime("%d %b %Y") if sel["date"] else "Select a date"
        )
        summary_guest_value.value = (
            f"{tickets['count']} guest" if tickets["count"] == 1 else f"{tickets['count']} guests"
        )
        if d and d.get("base_price") is not None:
            total = float(d["base_price"]) * tickets["count"]
            summary_total_value.value = f"Rs {total:,.0f}"
        else:
            summary_total_value.value = "Rs 0"

    def get_unavailable_dates():
        raw_dates = (activity_data["data"] or {}).get("unavailable_dates", []) or []
        parsed = set()

        for raw in raw_dates:
            try:
                parsed.add(date.fromisoformat(str(raw)))
            except Exception:
                pass

        return parsed

    def update_floating_reserve():
        if activity_data["data"] is None:
            floating_reserve_btn.visible = False
            return

        hide_after = max(booking_offset["value"] - 120, 0)
        floating_reserve_btn.visible = scroll_pixels["value"] < hide_after

    def handle_scroll(e):
        try:
            scroll_pixels["value"] = float(getattr(e, "pixels", 0) or 0)
        except Exception:
            scroll_pixels["value"] = 0.0
        update_floating_reserve()
        page.update()

    scroll_col.on_scroll = handle_scroll

    def build_calendar():
        y, m = current["year"], current["month"]
        month_label.value = datetime(y, m, 1).strftime("%B %Y")
        unavailable_dates = get_unavailable_dates()

        headers = ft.Row(
            controls=[
                ft.Container(
                    expand=True,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text(
                        d,
                        size=10,
                        color=MUTED,
                        weight=ft.FontWeight.W_600,
                    ),
                )
                for d in ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]
            ],
            spacing=0,
        )

        week_rows = []
        for week in calendar.monthcalendar(y, m):
            cells = []
            for day in week:
                if day == 0:
                    cells.append(ft.Container(expand=True, height=44))
                    continue

                d_obj = date(y, m, day)
                is_sel = sel["date"] == d_obj
                is_today = d_obj == today
                is_past = d_obj < today
                is_unavailable = d_obj in unavailable_dates and d_obj >= today
                is_disabled = is_past or is_unavailable

                def on_tap(e, _d=d_obj):
                    if _d < today or _d in unavailable_dates:
                        return
                    sel["date"] = _d
                    build_calendar()
                    refresh_book_btn()
                    refresh_booking_summary()
                    page.update()

                cells.append(
                    ft.Container(
                        expand=True,
                        height=44,
                        margin=ft.margin.only(left=2, right=2),
                        alignment=ft.Alignment(0, 0),
                        border_radius=14,
                        bgcolor=PRIMARY if is_sel else (UNAVAILABLE_BG if is_unavailable else CARD),
                        border=ft.Border.all(
                            1.5,
                            PRIMARY if is_sel else (
                                UNAVAILABLE_BORDER if is_unavailable else (
                                    TEAL if is_today and not is_sel else BORDER
                                )
                            ),
                        ),
                        on_click=on_tap if not is_disabled else None,
                        content=ft.Text(
                            str(day),
                            size=13,
                            text_align=ft.TextAlign.CENTER,
                            color="white" if is_sel else (
                                UNAVAILABLE_TEXT if is_unavailable else (
                                    MUTED if is_past else TEXT
                                )
                            ),
                            weight=ft.FontWeight.BOLD if (is_sel or is_today) else None,
                        ),
                    )
                )
            week_rows.append(ft.Row(cells, spacing=0))

        calendar_grid.controls = [headers, *week_rows]

    build_calendar()
    refresh_booking_summary()

    def prev_month(e):
        m, y = current["month"] - 1, current["year"]
        if m < 1:
            m, y = 12, y - 1
        if (y, m) < (today.year, today.month):
            return
        current["month"], current["year"] = m, y
        build_calendar()
        page.update()

    def next_month(e):
        m, y = current["month"] + 1, current["year"]
        if m > 12:
            m, y = 1, y + 1
        current["month"], current["year"] = m, y
        build_calendar()
        page.update()

    def decrement(e):
        if tickets["count"] > 1:
            tickets["count"] -= 1
            ticket_text.value = str(tickets["count"])
            refresh_book_btn()
            refresh_booking_summary()
            page.update()

    def increment(e):
        d = activity_data["data"]
        max_p = int(d.get("max_participants", 99)) if d else 99
        if tickets["count"] < max_p:
            tickets["count"] += 1
            ticket_text.value = str(tickets["count"])
            refresh_book_btn()
            refresh_booking_summary()
            page.update()

    def show_snack(msg, color=ERROR):
        snack = ft.SnackBar(content=ft.Text(msg), bgcolor=color)
        page.overlay.append(snack)
        snack.open = True
        page.update()

    def handle_book(e):
        if not sel["date"]:
            show_snack("Please select a date first.")
            return

        if sel["date"] in get_unavailable_dates():
            show_snack("This activity is already booked for the selected date.")
            return

        d = activity_data["data"]
        if not d:
            show_snack("Activity data is not ready yet. Please try again.")
            return

        total = float(d["base_price"]) * tickets["count"]
        page.session.store.set(
            "booking_data",
            {
                "activity_id": d["id"],
                "activity_name": d["name"],
                "date": str(sel["date"]),
                "num_people": tickets["count"],
                "base_price": d["base_price"],
                "total_price": total,
            },
        )
        page.go("/payment")

    async def _scroll_booking_async():
        try:
            await scroll_col.scroll_to(offset=booking_offset["value"], duration=550)
        except Exception:
            return
        scroll_pixels["value"] = booking_offset["value"]
        update_floating_reserve()
        page.update()

    def scroll_to_booking(e):
        page.run_task(_scroll_booking_async)

    def next_image():
        d = activity_data["data"]
        if not d:
            return
        images = d.get("images", [])
        if len(images) <= 1:
            return
        selected_image["index"] = (selected_image["index"] + 1) % len(images)
        build_page(d)
        page.update()

    def prev_image():
        d = activity_data["data"]
        if not d:
            return
        images = d.get("images", [])
        if len(images) <= 1:
            return
        selected_image["index"] = (selected_image["index"] - 1) % len(images)
        build_page(d)
        page.update()

    def on_hero_horizontal_drag_update(e):
        try:
            hero_drag_dx["value"] += float(getattr(e, "primary_delta", 0) or 0)
        except Exception:
            pass

    def on_hero_horizontal_drag_end(e):
        dx = hero_drag_dx["value"]
        hero_drag_dx["value"] = 0.0

        if abs(dx) < 20:
            return

        if dx < 0:
            next_image()
        else:
            prev_image()

    def toggle_description(e):
        description_expanded["value"] = not description_expanded["value"]
        if activity_data["data"] is not None:
            build_page(activity_data["data"])
            page.update()

    def build_page(d: dict):
        name = d.get("name", "Activity")
        location = d.get("location") or "Location not set"
        latitude = d.get("latitude")
        longitude = d.get("longitude")
        activity_type = d.get("activity_type", "Experience")
        duration = d.get("duration") or "—"
        max_p = d.get("max_participants", "—")
        description = d.get("description", "") or "No description available yet."
        avg_rating = d.get("avg_rating") or 0.0
        rev_count = d.get("review_count", 0)
        map_embed_url = d.get("map_embed_url", "")
        map_location_description = d.get("map_location_description", "")

        rules = [r for r in d.get("activity_rules", "").splitlines() if r.strip()]
        safety = [s for s in d.get("safety_equipment", "").splitlines() if s.strip()]
        cancellation = [c for c in d.get("cancellation_policy", "").splitlines() if c.strip()]

        images = d.get("images", [])
        highlights = d.get("highlights", [])
        reviews = d.get("reviews", [])

        unavailable_dates = set()
        for raw in d.get("unavailable_dates", []) or []:
            try:
                unavailable_dates.add(date.fromisoformat(str(raw)))
            except Exception:
                pass

        if sel["date"] in unavailable_dates:
            sel["date"] = None
            refresh_booking_summary()

        if images:
            if selected_image["index"] >= len(images):
                selected_image["index"] = 0
            hero_url = fix_image_url(images[selected_image["index"]].get("image_url"))
        else:
            hero_url = None

        short_description = description
        show_desc_toggle = len(description) > 240
        if show_desc_toggle and not description_expanded["value"]:
            short_description = description[:240].rsplit(" ", 1)[0] + "…"

        booking_offset["value"] = 970.0
        if highlights:
            booking_offset["value"] += 170.0
        if show_desc_toggle and description_expanded["value"]:
            booking_offset["value"] += 80.0

        hero_dots = ft.Container(height=0)
        if len(images) > 1:
            hero_dots = ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=6,
                controls=[
                    ft.Container(
                        width=9 if i == selected_image["index"] else 7,
                        height=9 if i == selected_image["index"] else 7,
                        border_radius=5,
                        bgcolor= TEAL if i == selected_image["index"] else "#80BFC7D5",
                    )
                    for i in range(len(images))
                ],
            )

        hero = ft.Container(
            height=360,
            content=ft.GestureDetector(
                drag_interval=0,
                on_horizontal_drag_update=on_hero_horizontal_drag_update,
                on_horizontal_drag_end=on_hero_horizontal_drag_end,
                content=ft.Stack(
                    expand=True,
                    controls=[
                        ft.Container(
                            expand=True,
                            bgcolor=HERO_FALLBACK,
                            clip_behavior=ft.ClipBehavior.HARD_EDGE,
                            content=(
                                ft.Image(
                                    src=hero_url,
                                    fit="cover",
                                    width=2000,
                                    height=2000,
                                    error_content=ft.Container(
                                        expand=True,
                                        alignment=ft.Alignment(0, 0),
                                        content=ft.Icon(ft.Icons.WAVES, size=70, color=TEAL),
                                    ),
                                )
                                if hero_url
                                else ft.Container(
                                    expand=True,
                                    alignment=ft.Alignment(0, 0),
                                    content=ft.Column(
                                        controls=[
                                            ft.Icon(ft.Icons.WAVES, size=72, color=TEAL),
                                            ft.Text("Ocean escape", color=PRIMARY, size=14),
                                        ],
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        spacing=8,
                                    ),
                                )
                            ),
                        ),
                        ft.Container(
                            expand=True,
                            gradient=ft.LinearGradient(
                                begin=ft.alignment.Alignment(0, -1),
                                end=ft.alignment.Alignment(0, 1),
                                colors=["#00000010", "#24000000", "#B3000000"],
                            ),
                        ),
                        ft.Container(
                            bottom=26,
                            left=18,
                            content=ft.Container(
                                border_radius=18,
                                bgcolor="#33FFFFFF",
                                padding=ft.padding.symmetric(horizontal=12, vertical=8),
                                content=ft.Text(
                                    activity_type,
                                    size=12,
                                    color="white",
                                    weight=ft.FontWeight.W_600,
                                ),
                            ),
                        ),
                        ft.Container(
                            bottom=40,
                            left=0,
                            right=0,
                            alignment=ft.Alignment(0, 0),
                            content=hero_dots if len(images) > 1 else ft.Container(height=0),
                        ),
                    ],
                ),
            ),
        )

        overview_section = soft_card(
            ft.Column(
                spacing=16,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                        controls=[
                            ft.Column(
                                expand=True,
                                spacing=8,
                                controls=[
                                    ft.Text(
                                        name,
                                        size=28,
                                        weight=ft.FontWeight.BOLD,
                                        color=TEXT,
                                    ),
                                    ft.Row(
                                        spacing=8,
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                        controls=[
                                            ft.Icon(ft.Icons.LOCATION_ON, size=16, color=TEAL),
                                            ft.Text(
                                                location,
                                                size=13,
                                                color=MUTED,
                                                max_lines=1,
                                                overflow=ft.TextOverflow.ELLIPSIS,
                                                expand=True,
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            ft.Container(
                                border_radius=18,
                                bgcolor=LIGHT,
                                padding=ft.padding.symmetric(horizontal=12, vertical=10),
                                content=ft.Column(
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=4,
                                    controls=[
                                        ft.Row(
                                            spacing=4,
                                            controls=[
                                                ft.Icon(ft.Icons.STAR, color=AMBER, size=16),
                                                ft.Text(
                                                    f"{avg_rating:.1f}" if avg_rating else "—",
                                                    size=14,
                                                    weight=ft.FontWeight.BOLD,
                                                    color=TEXT,
                                                ),
                                            ],
                                        ),
                                        ft.Text(
                                            f"{rev_count} reviews" if rev_count else "No reviews yet",
                                            size=11,
                                            color=MUTED,
                                        ),
                                    ],
                                ),
                            ),
                        ],
                    ),
                    star_row(avg_rating) if avg_rating else ft.Container(height=0),
                    ft.Row(
                        spacing=12,
                        controls=[
                            metric_card(ft.Icons.TIMELAPSE, "Duration", duration),
                            metric_card(ft.Icons.PEOPLE, "Group size", f"Up to {max_p}"),
                            metric_card(ft.Icons.WAVES, "Category", activity_type),
                        ],
                    ),
                ],
            ),
            margin=ft.margin.only(top=-28),
        )

        description_section = soft_card(
            ft.Column(
                spacing=14,
                controls=[
                    section_title("About this experience", "A quick feel for what to expect"),
                    ft.Text(
                        short_description,
                        size=13,
                        color=MUTED,
                        selectable=True,
                    ),
                    ft.TextButton(
                        "Read less" if description_expanded["value"] else "Read more",
                        on_click=toggle_description,
                    )
                    if show_desc_toggle
                    else ft.Container(height=0),
                    ft.Row(
                        wrap=True,
                        spacing=10,
                        controls=[
                            info_chip(ft.Icons.TIMELAPSE, duration, accent=True),
                            info_chip(ft.Icons.PEOPLE, f"Max {max_p} guests"),
                            info_chip(ft.Icons.WAVES, activity_type),
                        ],
                    ),
                ],
            )
        )

        highlights_section = ft.Container(height=0)
        if highlights:
            highlight_cards = []
            for h in highlights:
                highlight_cards.append(
                    ft.Container(
                        width=190,
                        border_radius=18,
                        bgcolor=LIGHT,
                        padding=ft.padding.all(16),
                        content=ft.Column(
                            spacing=12,
                            controls=[
                                ft.Container(
                                    width=46,
                                    height=46,
                                    border_radius=23,
                                    bgcolor=CARD,
                                    alignment=ft.Alignment(0, 0),
                                    content=(
                                        ft.Image(
                                            src=fix_image_url(h.get("icon_image_url")),
                                            width=26,
                                            height=26,
                                            fit="contain",
                                        )
                                        if h.get("icon_image_url")
                                        else ft.Icon(ft.Icons.STAR, size=20, color=TEAL)
                                    ),
                                ),
                                ft.Text(
                                    h.get("icon_title", ""),
                                    size=13,
                                    color=TEXT,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(
                                    h.get("icon_description", ""),
                                    size=12,
                                    color=MUTED,
                                    max_lines=3,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                            ],
                        ),
                    )
                )

            highlights_section = soft_card(
                ft.Column(
                    spacing=12,
                    controls=[
                        section_title("Why people love it", "The standout details of this experience"),
                        ft.Row(scroll=ft.ScrollMode.AUTO, spacing=12, controls=highlight_cards),
                    ],
                )
            )

        booking_section = soft_card(
            ft.Column(
                spacing=18,
                controls=[
                    ft.Column(
                        spacing=4,
                        controls=[
                            ft.Text(
                                "Reserve your experience",
                                size=22,
                                weight=ft.FontWeight.BOLD,
                                color=TEXT,
                            ),
                            ft.Text(
                                "Choose your date and group size before checking out.",
                                size=13,
                                color=MUTED,
                            ),
                        ],
                    ),
                    ft.Container(
                        border_radius=18,
                        bgcolor=LIGHT,
                        padding=ft.padding.all(16),
                        content=ft.Column(
                            spacing=12,
                            controls=[
                                ft.Text(
                                    "Booking summary",
                                    size=13,
                                    weight=ft.FontWeight.BOLD,
                                    color=TEXT,
                                ),
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Column(
                                            spacing=4,
                                            controls=[
                                                ft.Text("Date", size=11, color=MUTED),
                                                summary_date_value,
                                            ],
                                        ),
                                        ft.Column(
                                            spacing=4,
                                            horizontal_alignment=ft.CrossAxisAlignment.END,
                                            controls=[
                                                ft.Text("Guests", size=11, color=MUTED),
                                                summary_guest_value,
                                            ],
                                        ),
                                    ],
                                ),
                                ft.Divider(color=BORDER, height=1),
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text("Estimated total", size=12, color=MUTED),
                                        summary_total_value,
                                    ],
                                ),
                            ],
                        ),
                    ),
                    ft.Column(
                        spacing=10,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text(
                                        "Select date",
                                        size=15,
                                        weight=ft.FontWeight.BOLD,
                                        color=TEXT,
                                    ),
                                    ft.Row(
                                        spacing=4,
                                        controls=[
                                            ft.IconButton(
                                                ft.Icons.CHEVRON_LEFT,
                                                icon_color=TEXT,
                                                icon_size=20,
                                                on_click=prev_month,
                                            ),
                                            ft.IconButton(
                                                ft.Icons.CHEVRON_RIGHT,
                                                icon_color=TEXT,
                                                icon_size=20,
                                                on_click=next_month,
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            month_label,
                            calendar_grid,
                        ],
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(
                                spacing=4,
                                controls=[
                                    ft.Text(
                                        "Guests",
                                        size=15,
                                        weight=ft.FontWeight.BOLD,
                                        color=TEXT,
                                    ),
                                    ft.Text(
                                        f"Up to {max_p} guests per booking",
                                        size=12,
                                        color=MUTED,
                                    ),
                                ],
                            ),
                            ft.Container(
                                border_radius=18,
                                bgcolor=LIGHT,
                                padding=ft.padding.symmetric(horizontal=8, vertical=6),
                                content=ft.Row(
                                    spacing=6,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        ft.Container(
                                            width=36,
                                            height=36,
                                            border_radius=18,
                                            bgcolor=CARD,
                                            alignment=ft.Alignment(0, 0),
                                            on_click=decrement,
                                            content=ft.Icon(ft.Icons.REMOVE, size=18, color=MUTED),
                                        ),
                                        ft.Container(
                                            width=46,
                                            alignment=ft.Alignment(0, 0),
                                            content=ticket_text,
                                        ),
                                        ft.Container(
                                            width=36,
                                            height=36,
                                            border_radius=18,
                                            bgcolor=PRIMARY,
                                            alignment=ft.Alignment(0, 0),
                                            on_click=increment,
                                            content=ft.Icon(ft.Icons.ADD, size=18, color="white"),
                                        ),
                                    ],
                                ),
                            ),
                        ],
                    ),
                    ft.Container(
                        height=56,
                        border_radius=28,
                        bgcolor=PRIMARY,
                        alignment=ft.Alignment(0, 0),
                        on_click=handle_book,
                        content=book_btn_text,
                    ),
                ],
            ),
            margin=ft.margin.symmetric(horizontal=12, vertical=10),
        )

        maps_url = (
            map_embed_url.strip()
            or (f"https://www.google.com/maps/search/?api=1&query={quote_plus(location)}" if location else "")
        )

        map_section = ft.Container(height=0)
        if latitude is not None and longitude is not None:
            map_section = soft_card(
                ft.Column(
                    spacing=14,
                    controls=[
                        section_title(
                            "Location",
                            map_location_description or "Find where this experience starts.",
                        ),
                        ft.Container(
                            height=220,
                            border_radius=18,
                            clip_behavior=ft.ClipBehavior.HARD_EDGE,
                            content=ftm.Map(
                                expand=True,
                                initial_center=ftm.MapLatitudeLongitude(latitude, longitude),
                                initial_zoom=13,
                                interaction_configuration=ftm.InteractionConfiguration(
                                    flags=ftm.InteractionFlag.ALL
                                ),
                                layers=[
                                    ftm.TileLayer(
                                        url_template="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
                                        subdomains=["a", "b", "c", "d"],
                                    ),
                                    ftm.MarkerLayer(
                                        markers=[
                                            ftm.Marker(
                                                coordinates=ftm.MapLatitudeLongitude(latitude, longitude),
                                                content=ft.Icon(
                                                    ft.Icons.LOCATION_ON,
                                                    color=PRIMARY,
                                                    size=30,
                                                ),
                                            )
                                        ]
                                    ),
                                ],
                            ),
                        ),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Row(
                                    spacing=8,
                                    controls=[
                                        ft.Icon(ft.Icons.LOCATION_ON, color=TEAL, size=18),
                                        ft.Text(location or "Location not set", color=TEXT, size=13),
                                    ],
                                ),
                            ],
                        ),
                    ],
                )
            )
        else:
            map_section = soft_card(
                ft.Column(
                    spacing=12,
                    controls=[
                        section_title(
                            "Location",
                            map_location_description or "Location details for this experience.",
                        ),
                        ft.Container(
                            height=120,
                            border_radius=18,
                            bgcolor=LIGHT,
                            alignment=ft.Alignment(0, 0),
                            content=ft.Column(
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=8,
                                controls=[
                                    ft.Icon(ft.Icons.LOCATION_ON, color=TEAL, size=34),
                                    ft.Text(location or "Location not set", color=TEXT, size=14),
                                    ft.Text(
                                        "Add latitude and longitude to show the live map here.",
                                        color=MUTED,
                                        size=12,
                                        text_align=ft.TextAlign.CENTER,
                                    ),
                                ],
                            ),
                        ),
                    ],
                )
            )

        rules_section = bullet_section(
            "Activity rules",
            rules,
            ft.Icons.CIRCLE,
            PRIMARY,
            "Tap to view all rules",
            section_key="rules",
        )

        safety_section = bullet_section(
            "Safety & equipment",
            safety,
            ft.Icons.SHIELD,
            TEAL,
            "Tap to view all safety details",
            section_key="safety",
        )

        cancellation_section = bullet_section(
            "Cancellation policy",
            cancellation,
            ft.Icons.INFO_OUTLINE,
            ORANGE,
            "Tap to view policy details",
            section_key="cancellation",
        )

        if reviews:
            reviews_body = ft.Column(
                spacing=12,
                controls=[review_card(r) for r in reviews[:6]],
            )
            reviews_subtitle = (
                f"{avg_rating:.1f} average rating across {rev_count} review{'s' if rev_count != 1 else ''}"
                if rev_count
                else "Tap to view guest reviews"
            )
        else:
            reviews_body = ft.Container(
                border_radius=18,
                bgcolor=LIGHT,
                padding=ft.padding.all(18),
                content=ft.Text(
                    "No reviews yet, but this experience is ready for its first guests.",
                    size=13,
                    color=MUTED,
                ),
            )
            reviews_subtitle = "Be the first to leave a review after your experience"

        reviews_section = soft_card(
            ft.ExpansionTile(
                expanded=expanded_sections.get("reviews", False),
                maintain_state=True,
                on_change=handle_expansion_change("reviews"),
                tile_padding=ft.padding.all(0),
                controls_padding=ft.padding.only(top=8, bottom=0, left=0, right=0),
                icon_color=MUTED,
                collapsed_icon_color=MUTED,
                text_color=TEXT,
                collapsed_text_color=TEXT,
                shape=ft.RoundedRectangleBorder(
                    radius=16,
                    side=ft.BorderSide.none(),
                ),
                collapsed_shape=ft.RoundedRectangleBorder(
                    radius=16,
                    side=ft.BorderSide.none(),
                ),
                leading=ft.Container(
                    width=34,
                    height=34,
                    border_radius=17,
                    bgcolor=LIGHT,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Icon(ft.Icons.RATE_REVIEW, size=16, color=TEAL),
                ),
                title=ft.Text(
                    "Guest reviews",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=TEXT,
                ),
                subtitle=ft.Text(
                    reviews_subtitle,
                    size=12,
                    color=MUTED,
                ),
                controls=[reviews_body],
            ),
            padding=16,
        )

        scroll_col.controls = [
            hero,
            ft.Container(
                bgcolor=BG,
                padding=ft.padding.symmetric(horizontal=14, vertical=0),
                content=ft.Column(
                    spacing=0,
                    controls=[
                        overview_section,
                        ft.Container(height=12),
                        description_section,
                        ft.Container(height=12),
                        highlights_section if highlights else ft.Container(height=0),
                        ft.Container(height=12 if highlights else 0),
                        booking_section,
                        ft.Container(height=12),
                        map_section,
                        ft.Container(height=12),
                        rules_section if rules else ft.Container(height=0),
                        ft.Container(height=12 if rules else 0),
                        safety_section if safety else ft.Container(height=0),
                        ft.Container(height=12 if safety else 0),
                        cancellation_section if cancellation else ft.Container(height=0),
                        ft.Container(height=12 if cancellation else 0),
                        reviews_section,
                        ft.Container(height=120),
                    ],
                ),
            ),
        ]

        update_floating_reserve()

    def fetch():
        try:
            resp = requests.get(
                f"{BASE_URL}/api/activities/{activity_id}/",
                timeout=10,
            )
            resp.raise_for_status()
            d = resp.json()
            activity_data["data"] = d
            build_calendar()
            refresh_book_btn()
            refresh_booking_summary()
            build_page(d)
        except requests.ConnectionError:
            _show_error(
                "Cannot connect to server.\nMake sure Django is running on port 8000."
            )
        except requests.HTTPError as exc:
            _show_error(f"Server returned {exc.response.status_code}")
        except Exception as exc:
            _show_error(str(exc))
        page.update()

    def _show_error(msg: str):
        floating_reserve_btn.visible = False
        scroll_col.controls = [
            ft.Container(
                height=700,
                alignment=ft.Alignment(0, 0),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=14,
                    controls=[
                        ft.Container(
                            width=78,
                            height=78,
                            border_radius=39,
                            bgcolor="#FEE2E2",
                            alignment=ft.Alignment(0, 0),
                            content=ft.Icon(ft.Icons.ERROR_OUTLINE, color=ERROR, size=42),
                        ),
                        ft.Text(
                            "Something went wrong",
                            size=18,
                            color=TEXT,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            msg,
                            color=MUTED,
                            size=13,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Container(
                            border_radius=22,
                            bgcolor=PRIMARY,
                            padding=ft.padding.symmetric(horizontal=18, vertical=10),
                            on_click=lambda e: page.run_thread(fetch),
                            content=ft.Text(
                                "Retry",
                                size=13,
                                color="white",
                                weight=ft.FontWeight.W_600,
                            ),
                        ),
                    ],
                ),
            )
        ]

    fixed_back_btn = ft.Container(
        top=48,
        left=16,
        width=46,
        height=46,
        border_radius=23,
        bgcolor="#66FFFFFF",
        alignment=ft.Alignment(0, 0),
        shadow=ft.BoxShadow(
            blur_radius=12,
            spread_radius=0,
            color="#18000000",
            offset=ft.Offset(0, 4),
        ),
        on_click=lambda e: page.go("/home"),
        content=ft.Icon(
            ft.Icons.ARROW_BACK_IOS_NEW,
            color=PRIMARY,
            size=18,
        ),
    )

    floating_reserve_btn = ft.Container(
        visible=False,
        left=0,
        right=0,
        bottom=40,
        alignment=ft.Alignment(0, 0),
        content=ft.Container(
            height=56,
            width=220,
            border_radius=28,
            bgcolor=PRIMARY,
            shadow=ft.BoxShadow(
                blur_radius=18,
                spread_radius=0,
                color="#22000000",
                offset=ft.Offset(0, 8),
            ),
            on_click=scroll_to_booking,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
                controls=[
                    ft.Text(
                        "Reserve now",
                        color="white",
                        size=16,
                        weight=ft.FontWeight.W_600,
                    ),
                    ft.Icon(ft.Icons.ARROW_FORWARD, color="white", size=18),
                ],
            ),
        ),
    )

    page.run_thread(fetch)

    return ft.View(
        route=f"/activity/{activity_id}",
        bgcolor=BG,
        padding=0,
        controls=[
            ft.Stack(
                expand=True,
                controls=[
                    ft.Container(expand=True, content=scroll_col),
                    fixed_back_btn,
                    floating_reserve_btn,
                ],
            )
        ],
    )