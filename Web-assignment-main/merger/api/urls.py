from .views import *
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    PaymentViewSet,
    ActivityListView,
    ActivityDetailView,
    BookingCreateView
)

router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payments')


urlpatterns = [
    path("signup/", signup_api),
    path("login/", login_api),
    path("activities/", activities_api),
    path("bookings/<int:user_id>/", user_bookings_api),
    path("create-booking/", create_booking_api),
    path("payment/", payment_api),
    path("review/", review_api),
    path("profile/<int:user_id>/", profile_update_api),
    path("notifications/<int:user_id>/", notifications_api),
    path("bookings/<int:booking_id>/cancel/", cancel_booking_api),
    path("", include(router.urls)),
    path("activities/", ActivityListView.as_view()),
    path("activities/<int:pk>/", ActivityDetailView.as_view()),
    path("bookings/", BookingCreateView.as_view())
]
