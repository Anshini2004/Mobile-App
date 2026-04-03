from django.urls import path
from .views import *

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
    path("bookings/<int:booking_id>/cancel/", cancel_booking_api)
]