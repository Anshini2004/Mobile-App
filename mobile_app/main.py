import flet as ft

# ── Design tokens ──────────────────────────────────────────────────────────────
TEAL        = "#3BBFB2"
TEAL_LIGHT  = "#E8F8F7"
BG          = "#F4F7F7"
CARD_BG     = "#FFFFFF"
TEXT_DARK   = "#1A2E2D"
TEXT_MUTED  = "#7B9492"
BORDER      = "#DDE8E7"

STATUS_CFG = {
    "CONFIRMED": {"bg": "#E6F9F0", "fg": "#1A9B5F", "label": "Confirmed"},
    "COMPLETED": {"bg": "#E8F0FE", "fg": "#1A5FBB", "label": "Completed"},
    "CANCELLED": {"bg": "#FDE8E8", "fg": "#C0392B", "label": "Cancelled"},
}

BOOKINGS = [
    {"id": "BK-001", "activity": "Catamaran Sunset Cruise", "icon": ft.Icons.SAILING, "date": "Thu, 10 Apr 2026", "time": "05:30 PM", "tickets": 2, "price": 4500, "status": "CONFIRMED"},
    {"id": "BK-004", "activity": "Snorkeling at Blue Bay", "icon": ft.Icons.WAVES, "date": "Sat, 25 Apr 2026", "time": "11:00 AM", "tickets": 4, "price": 2800, "status": "CONFIRMED"},
    {"id": "BK-002", "activity": "Scuba Diving – Beginner", "icon": ft.Icons.POOL, "date": "Fri, 20 Mar 2026", "time": "10:30 AM", "tickets": 1, "price": 6000, "status": "COMPLETED"},
    {"id": "BK-005", "activity": "Deep-Sea Fishing Trip", "icon": ft.Icons.ANCHOR, "date": "Sun, 08 Mar 2026", "time": "06:00 AM", "tickets": 3, "price": 7500, "status": "COMPLETED"},
    {"id": "BK-003", "activity": "Dolphin Watching", "icon": ft.Icons.WATER, "date": "Sun, 15 Feb 2026", "time": "07:00 AM", "tickets": 3, "price": 3000, "status": "CANCELLED"},
    {"id": "BK-006", "activity": "Glass-Bottom Boat Tour", "icon": ft.Icons.DIRECTIONS_BOAT, "date": "Tue, 03 Feb 2026", "time": "02:00 PM", "tickets": 2, "price": 1800, "status": "CANCELLED"},
]

CENTER = ft.Alignment(0, 0)

def pad_all(v): return ft.Padding(v, v, v, v)
def pad_sym(h=0, v=0): return ft.Padding(h, v, h, v)
def pad_only(left=0, right=0, top=0, bottom=0): return ft.Padding(left, top, right, bottom)

def main(page: ft.Page):
    page.title = "My Bookings"
    page.bgcolor = BG
    page.window.width, page.window.height = 550, 900

    dialog = ft.AlertDialog(title=ft.Text("Confirm Cancellation"), modal=True)
    page.dialog = dialog

    def close_dialog():
        dialog.open = False
        page.update()

    filter_pills_row = ft.Ref[ft.Row]()
    cards_column = ft.Ref[ft.Column]()

    active_filter = {"value": "ALL"}

    # ── Booking helpers ─────────────────────────────────────────────────────
    def chip(icon, text: str):
        return ft.Row(spacing=4, controls=[ft.Icon(icon, size=13, color=TEXT_MUTED), ft.Text(text, size=11, color=TEXT_MUTED)])

    def booking_card(b: dict):
        tickets_label = f"{b['tickets']} ticket{'s' if b['tickets'] > 1 else ''}"
        row_controls = [
            ft.Row(
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        content=ft.Icon(b["icon"], size=20, color=TEAL),
                        width=44, height=44,
                        bgcolor=TEAL_LIGHT,
                        border_radius=22,
                        alignment=CENTER,
                    ),
                    ft.Column(
                        spacing=2,
                        expand=True,
                        controls=[
                            ft.Text(b["activity"], size=14, weight=ft.FontWeight.W_700,
                                    color=TEXT_DARK, overflow=ft.TextOverflow.ELLIPSIS, max_lines=1),
                            ft.Text(b["id"], size=11, color=TEXT_MUTED),
                        ],
                    ),
                ],
            )
        ]

        if b["status"] == "CONFIRMED":
            def on_cancel_click(_e):
                def on_confirm(e):
                    b["status"] = "CANCELLED"
                    rebuild_cards()
                    page.update()
                    dialog.open = False
                    page.update()
                dialog.content = ft.Column(spacing=10, controls=[
                    ft.Text(f"Are you sure you want to cancel '{b['activity']}'?", size=14),
                    ft.Row(spacing=10, controls=[
                        ft.Button("Yes, Cancel", on_click=on_confirm, bgcolor="#8B1A1A", height=36),
                        ft.Button("No", on_click=lambda e: close_dialog(), bgcolor=TEAL, height=36),
                    ])
                ])
                dialog.open = True
                page.update()
            row_controls.append(
                ft.Container(
                    content=ft.Button("Cancel", on_click=on_cancel_click, bgcolor="#8B1A1A", height=32),
                    padding=pad_sym(h=8, v=2),
                    alignment=CENTER,
                )
            )

        controls = [
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=row_controls
            ),
            ft.Divider(height=1, thickness=1, color=BORDER),
            ft.Row(spacing=14, wrap=True, controls=[
                chip(ft.Icons.CALENDAR_TODAY, b["date"]),
                chip(ft.Icons.SCHEDULE, b["time"]),
                chip(ft.Icons.CONFIRMATION_NUMBER, tickets_label),
            ]),
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text("Total paid", size=11, color=TEXT_MUTED),
                    ft.Text(f"Rs {b['price']:,}", size=15, weight=ft.FontWeight.W_700, color=TEXT_DARK),
                ],
            )
        ]

        return ft.Container(
            bgcolor=CARD_BG,
            border_radius=16,
            padding=pad_all(12),
            shadow=ft.BoxShadow(blur_radius=12, color="#14000000", offset=ft.Offset(0, 4)),
            content=ft.Column(spacing=10, controls=controls)
        )

    def make_pill(label: str, value: str):
        is_active = value == active_filter["value"]
        def on_tap(_e, v=value):
            active_filter["value"] = v
            rebuild_pills()
            rebuild_cards()
            page.update()
        return ft.GestureDetector(
            on_tap=on_tap,
            content=ft.Container(
                content=ft.Text(label, size=12, weight=ft.FontWeight.W_600,
                                color=ft.Colors.WHITE if is_active else TEXT_MUTED),
                bgcolor=TEAL if is_active else CARD_BG,
                border_radius=20,
                padding=pad_sym(h=16, v=8),
                border=None if is_active else ft.border.all(1, BORDER),
                animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
            )
        )

    def rebuild_pills():
        filter_pills_row.current.controls = [
            make_pill("All", "ALL"),
            make_pill("Upcoming", "CONFIRMED"),
            make_pill("Completed", "COMPLETED"),
            make_pill("Cancelled", "CANCELLED"),
        ]

    def rebuild_cards():
        f = active_filter["value"]
        filtered = BOOKINGS if f == "ALL" else [b for b in BOOKINGS if b["status"] == f]

        if filtered:
            items = [ft.Container(content=booking_card(b), padding=pad_sym(h=16, v=6)) for b in filtered]
        else:
            items = [ft.Container(padding=pad_only(top=60), alignment=CENTER, content=ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8, controls=[
                ft.Icon(ft.Icons.INBOX_OUTLINED, size=52, color=BORDER),
                ft.Text("No bookings found", size=14, color=TEXT_MUTED, weight=ft.FontWeight.W_500),
            ]))]
        cards_column.current.controls = items

    # ── Stats ────────────────────────────────────────────────────────────────
    def stat_tile(value: str, label: str, color: str):
        return ft.Container(
            expand=True,
            padding=pad_sym(h=6, v=12),
            bgcolor=CARD_BG,
            border_radius=14,
            border=ft.border.all(1, BORDER),
            content=ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=3, tight=True, controls=[
                ft.Text(value, size=19, weight=ft.FontWeight.W_800, color=color),
                ft.Text(label, size=10, color=TEXT_MUTED, text_align=ft.TextAlign.CENTER),
            ])
        )

    confirmed = sum(1 for b in BOOKINGS if b["status"] == "CONFIRMED")
    completed = sum(1 for b in BOOKINGS if b["status"] == "COMPLETED")
    total_spent = sum(b["price"] for b in BOOKINGS if b["status"] != "CANCELLED")

    # ── Header ───────────────────────────────────────────────────────────────
    header = ft.Container(
        bgcolor=CARD_BG,
        padding=pad_only(left=20, right=20, top=52, bottom=16),
        shadow=ft.BoxShadow(blur_radius=8, color="#0F000000", offset=ft.Offset(0, 2)),
        content=ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
            ft.Column(spacing=2, tight=True, controls=[
                ft.Text("My Bookings", size=22, weight=ft.FontWeight.W_800, color=TEXT_DARK),
                ft.Text(f"{len(BOOKINGS)} reservations", size=12, color=TEXT_MUTED),
            ]),
            ft.Container(content=ft.Icon(ft.Icons.NOTIFICATIONS_NONE, size=20, color=TEXT_DARK), width=38, height=38, bgcolor=TEAL_LIGHT, border_radius=19, alignment=CENTER),
        ]),
    )

    # ── Scrollable middle content (stats + filter pills + cards) ─────────────
    middle_content = ft.Column(
        expand=True,
        scroll="auto",
        spacing=0,
        controls=[
            ft.Container(
                padding=pad_only(left=16, right=16, top=14, bottom=6),
                content=ft.Row(spacing=10, controls=[
                    stat_tile(str(confirmed), "Upcoming", TEAL),
                    stat_tile(str(completed), "Completed", "#1A5FBB"),
                    stat_tile(f"Rs {total_spent:,}", "Total Spent", TEXT_DARK),
                ])
            ),
            ft.Container(padding=pad_sym(h=16, v=8), content=ft.Row(ref=filter_pills_row, spacing=8, controls=[])),
            ft.Column(ref=cards_column, spacing=0, controls=[]),
        ]
    )

    # ── Bottom nav (always fixed) ─────────────────────────────────────────────
    def nav_btn(icon, label: str, active: bool = False):
        return ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=3, tight=True, controls=[
            ft.Icon(icon, size=21, color=TEAL if active else TEXT_MUTED),
            ft.Text(label, size=9, color=TEAL if active else TEXT_MUTED, weight=ft.FontWeight.W_600 if active else ft.FontWeight.W_400),
        ])

    bottom_nav = ft.Container(
        bgcolor=CARD_BG,
        border=ft.Border.only(top=ft.BorderSide(1, BORDER)),
        padding=pad_sym(h=8, v=10),
        content=ft.Row(alignment=ft.MainAxisAlignment.SPACE_AROUND, controls=[
            nav_btn(ft.Icons.GRID_VIEW, "Catalogue"),
            nav_btn(ft.Icons.FAVORITE_BORDER, "Wishlist"),
            nav_btn(ft.Icons.FEED_OUTLINED, "Feed"),
            nav_btn(ft.Icons.CONFIRMATION_NUMBER, "My Bookings", active=True),
            nav_btn(ft.Icons.PERSON_OUTLINE, "Profile"),
        ])
    )

    # ── Add all to page ──────────────────────────────────────────────────────
    page.add(ft.Column(
        expand=True,
        spacing=0,
        controls=[
            header,
            middle_content,
            bottom_nav
        ]
    ))

    rebuild_pills()
    rebuild_cards()
    page.update()

ft.run(main)