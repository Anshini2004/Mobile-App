# views/booking_view.py

import flet as ft
from api.booking_api import get_bookings, cancel_booking
from utils.constants import *
from views.components import chip, stat_tile, nav_btn


def bookings_page(page: ft.Page):

    # ── Loading / error states ────────────────────────────────────────────────
    loading_indicator = ft.Container(
        padding=pad_only(top=60),
        alignment=CENTER,
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
            controls=[
                ft.ProgressRing(color=TEAL, width=36, height=36),
                ft.Text("Loading your bookings…", size=13, color=TEXT_MUTED),
            ],
        ),
    )

    error_banner = ft.Container(
        padding=pad_only(top=60),
        alignment=CENTER,
        visible=False,
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
            controls=[
                ft.Icon(ft.Icons.WIFI_OFF, size=48, color=BORDER),
                ft.Text(
                    "Could not load bookings",
                    size=14,
                    color=TEXT_MUTED,
                    weight=ft.FontWeight.W_500,
                ),
                ft.Text(
                    "Check your connection and try again.",
                    size=11,
                    color=TEXT_MUTED,
                ),
            ],
        ),
    )

    BOOKINGS: list[dict] = []
    active_filter = {"value": "ALL"}

    # ── Dialog / Popup ────────────────────────────────────────────────────────
    # Flet requires title/content/actions to exist when the dialog is created.
    dialog = ft.AlertDialog(
        modal=True,
        bgcolor=ft.Colors.TRANSPARENT,
        barrier_color=ft.Colors.with_opacity(0.45, ft.Colors.BLACK),
        content=ft.Container(width=1, height=1),  # placeholder to avoid error
    )
    page.overlay.append(dialog)

    def close_dialog(e=None):
        dialog.open = False
        page.update()

    filter_pills_row = ft.Ref[ft.Row]()
    cards_column = ft.Ref[ft.Column]()
    stats_row = ft.Ref[ft.Row]()

    # ── Booking card ──────────────────────────────────────────────────────────
    def booking_card(b: dict):
        tickets_label = f"{b['tickets']} ticket{'s' if b['tickets'] > 1 else ''}"

        row_controls = [
            ft.Row(
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        content=ft.Icon(b["icon"], size=20, color=TEAL),
                        width=44,
                        height=44,
                        bgcolor=TEAL_LIGHT,
                        border_radius=22,
                        alignment=CENTER,
                    ),
                    ft.Column(
                        spacing=2,
                        expand=True,
                        controls=[
                            ft.Text(
                                b["activity"],
                                size=14,
                                weight=ft.FontWeight.W_700,
                                color=TEXT_DARK,
                                overflow=ft.TextOverflow.ELLIPSIS,
                                max_lines=1,
                            ),
                            ft.Text(b["id"], size=11, color=TEXT_MUTED),
                        ],
                    ),
                ],
            )
        ]

        if b["status"] == "CONFIRMED":

            async def on_cancel_click(e, booking=b):

                async def on_confirm(e):
                    # optimistic UI update
                    booking["status"] = "CANCELLED"
                    rebuild_cards()
                    rebuild_stats()
                    rebuild_pills()
                    dialog.open = False
                    page.update()

                    # backend call
                    success = await cancel_booking(page, booking["db_id"])

                    # rollback if failed
                    if not success:
                        booking["status"] = "CONFIRMED"
                        rebuild_cards()
                        rebuild_stats()
                        rebuild_pills()
                        page.update()

                # ── NICE POPUP UI ──
                dialog.content = ft.Container(
                    width=280,  # smaller width
                    padding=12,  # reduced padding
                    border_radius=14,
                    bgcolor=ft.Colors.WHITE,
                    shadow=ft.BoxShadow(
                        blur_radius=18,
                        color="#22000000",
                        offset=ft.Offset(0, 6),
                    ),
                    content=ft.Column(
                        spacing=8,  # tighter spacing
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        tight=True,
                        controls=[
                            ft.Container(
                                width=40,
                                height=40,
                                border_radius=20,
                                bgcolor="#FCE8E8",
                                alignment=CENTER,
                                content=ft.Icon(
                                    ft.Icons.WARNING_AMBER_ROUNDED,
                                    size=22,  # smaller icon
                                    color="#8B1A1A",
                                ),
                            ),
                            ft.Text(
                                "Cancel booking?",
                                size=15,  # smaller title
                                weight=ft.FontWeight.BOLD,
                                text_align=ft.TextAlign.CENTER,
                                color=ft.Colors.BLACK,
                            ),
                            ft.Text(
                                f"Cancel '{b['activity']}'?",
                                size=11,  # smaller text
                                text_align=ft.TextAlign.CENTER,
                                color=TEXT_MUTED,
                                max_lines=2,
                            ),
                            ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=6,  # tighter buttons
                                controls=[
                                    ft.ElevatedButton(
                                        "Yes",
                                        on_click=on_confirm,
                                        style=ft.ButtonStyle(
                                            bgcolor="#8B1A1A",
                                            color=ft.Colors.WHITE,
                                            padding=ft.Padding(10, 6, 10, 6),
                                            shape=ft.RoundedRectangleBorder(radius=8),
                                        ),
                                    ),
                                    ft.TextButton(
                                        "No",
                                        on_click=close_dialog,
                                        style=ft.ButtonStyle(
                                            padding=ft.Padding(10, 6, 10, 6),
                                            color=TEXT_DARK,
                                        ),
                                    ),
                                ],
                            ),
                        ],
                    ),
                )
                dialog.open = True
                page.update()

            row_controls.append(
                ft.Container(
                    content=ft.ElevatedButton(
                        "Cancel",
                        on_click=on_cancel_click,
                        style=ft.ButtonStyle(
                            bgcolor="#8B1A1A",
                            color=ft.Colors.WHITE,
                            shape=ft.RoundedRectangleBorder(radius=10),
                        ),
                    ),
                    padding=pad_sym(h=8, v=2),
                    alignment=CENTER,
                )
            )

        return ft.Container(
            bgcolor=CARD_BG,
            border_radius=16,
            padding=pad_all(12),
            shadow=ft.BoxShadow(
                blur_radius=12,
                color="#14000000",
                offset=ft.Offset(0, 4),
            ),
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=row_controls,
                    ),
                    ft.Divider(height=1, thickness=1, color=BORDER),
                    ft.Row(
                        spacing=14,
                        wrap=True,
                        controls=[
                            chip(ft.Icons.CALENDAR_TODAY, b["date"]),
                            chip(ft.Icons.CONFIRMATION_NUMBER, tickets_label),
                        ],
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("Total paid", size=11, color=TEXT_MUTED),
                            ft.Text(
                                f"Rs {b['price']:,.0f}",
                                size=15,
                                weight=ft.FontWeight.W_700,
                                color=TEXT_DARK,
                            ),
                        ],
                    ),
                ],
            ),
        )

    # ── Pills ─────────────────────────────────────────────────────────────────
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
                content=ft.Text(
                    label,
                    size=12,
                    weight=ft.FontWeight.W_600,
                    color=ft.Colors.WHITE if is_active else TEXT_MUTED,
                ),
                bgcolor=TEAL if is_active else CARD_BG,
                border_radius=20,
                padding=pad_sym(h=16, v=8),
                border=None if is_active else ft.Border.all(1, BORDER),
                animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
            ),
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
            items = [
                ft.Container(content=booking_card(b), padding=pad_sym(h=16, v=6))
                for b in filtered
            ]
        else:
            items = [
                ft.Container(
                    padding=pad_only(top=60),
                    alignment=CENTER,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.INBOX_OUTLINED, size=52, color=BORDER),
                            ft.Text(
                                "No bookings found",
                                size=14,
                                color=TEXT_MUTED,
                                weight=ft.FontWeight.W_500,
                            ),
                        ],
                    ),
                )
            ]
        cards_column.current.controls = items

    def rebuild_stats():
        confirmed = sum(1 for b in BOOKINGS if b["status"] == "CONFIRMED")
        completed = sum(1 for b in BOOKINGS if b["status"] == "COMPLETED")
        total_spent = sum(b["price"] for b in BOOKINGS if b["status"] != "CANCELLED")
        stats_row.current.controls = [
            stat_tile(str(confirmed), "Upcoming", TEAL),
            stat_tile(str(completed), "Completed", "#1A5FBB"),
            stat_tile(f"Rs {total_spent:,.0f}", "Total Spent", TEXT_DARK),
        ]

    # ── Header ────────────────────────────────────────────────────────────────
    header_subtitle = ft.Text("Loading…", size=12, color=TEXT_MUTED)
    header = ft.Container(
        bgcolor=CARD_BG,
        padding=pad_only(left=20, right=20, top=52, bottom=16),
        shadow=ft.BoxShadow(blur_radius=8, color="#0F000000", offset=ft.Offset(0, 2)),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Column(
                    spacing=2,
                    tight=True,
                    controls=[
                        ft.Text(
                            "My Bookings",
                            size=22,
                            weight=ft.FontWeight.W_800,
                            color=TEXT_DARK,
                        ),
                        header_subtitle,
                    ],
                ),
                ft.Container(
                    content=ft.Icon(ft.Icons.NOTIFICATIONS_NONE, size=20, color=TEXT_DARK),
                    width=38,
                    height=38,
                    bgcolor=TEAL_LIGHT,
                    border_radius=19,
                    alignment=CENTER,
                ),
            ],
        ),
    )

    # ── Scrollable body ───────────────────────────────────────────────────────
    middle_content = ft.Column(
        expand=True,
        scroll="auto",
        spacing=0,
        controls=[
            ft.Container(
                padding=pad_only(left=16, right=16, top=14, bottom=6),
                content=ft.Row(
                    ref=stats_row,
                    spacing=10,
                    controls=[
                        stat_tile("–", "Upcoming", TEAL),
                        stat_tile("–", "Completed", "#1A5FBB"),
                        stat_tile("Rs –", "Total Spent", TEXT_DARK),
                    ],
                ),
            ),
            ft.Container(
                padding=pad_sym(h=16, v=8),
                content=ft.Row(ref=filter_pills_row, spacing=8, controls=[]),
            ),
            loading_indicator,
            error_banner,
            ft.Column(ref=cards_column, spacing=0, controls=[]),
            ft.Container(height=100),
        ],
    )

    layout = ft.Column(
        expand=True,
        spacing=0,
        controls=[header, middle_content],
    )

    rebuild_pills()

    # ── async data loader — this is what Flet requires ───────────────────────
    async def load_data():
        nonlocal BOOKINGS
        try:
            BOOKINGS = await get_bookings(page)
            loading_indicator.visible = False
            error_banner.visible = False
            header_subtitle.value = (
                f"{len(BOOKINGS)} reservation{'s' if len(BOOKINGS) != 1 else ''}"
            )
            rebuild_stats()
            rebuild_pills()
            rebuild_cards()
        except Exception as exc:
            print(f"[bookings_page] load_data error: {exc}")
            loading_indicator.visible = False
            error_banner.visible = True
        finally:
            page.update()

    page.run_task(load_data)

    return layout
