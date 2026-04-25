from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    PaymentViewSet,
    ActivityListView,
    ActivityDetailView,
    BookingCreateView,
    ActivityViewSet,
    UserViewSet,
    AuthViewSet,
    NearMeActivityViewSet,
    user_bookings_api,
    cancel_booking_api,
    review_api,
    notifications_api,
    current_user,
)

router = DefaultRouter()
router.register(r"payments", PaymentViewSet, basename="payments")
router.register(r"users", UserViewSet, basename="user")
router.register(r"activities-catalogue", ActivityViewSet, basename="activity-catalogue")
router.register(r"auth", AuthViewSet, basename="auth")
router.register(r"nearmeactivity", NearMeActivityViewSet, basename="nearme")

urlpatterns = [
    # JWT auth
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Activities
    path("activities/", ActivityListView.as_view(), name="activity-list"),
    path("activities/<int:pk>/", ActivityDetailView.as_view(), name="activity-detail"),

    # Bookings
    path("bookings/<int:user_id>/", user_bookings_api, name="user-bookings"),
    path("bookings/<int:booking_id>/cancel/", cancel_booking_api, name="cancel-booking"),
    path("bookings/", BookingCreateView.as_view(), name="booking-create"),

    # Reviews / notifications / profile
    path("review/", review_api, name="review"),
    path("notifications/<int:user_id>/", notifications_api, name="notifications"),
    path("userprofile/", current_user, name="userprofile"),

    # ViewSets
    path("", include(router.urls)),
]