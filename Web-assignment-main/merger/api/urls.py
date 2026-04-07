from django.urls import path
from .views import (
    process_payment,
    ActivityListView,
    ActivityDetailView,
    BookingCreateView,
)

urlpatterns = [
    # POST /api/payment/
    path("payment/", process_payment, name="payment"),

    # GET  /api/activities/
    path("activities/", ActivityListView.as_view(), name="activity-list"),

    # GET  /api/activities/<pk>/
    path("activities/<int:pk>/", ActivityDetailView.as_view(), name="activity-detail"),

    # POST /api/bookings/
    path("bookings/", BookingCreateView.as_view(), name="booking-create"),
]