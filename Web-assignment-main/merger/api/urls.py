from django.urls import path
from . import views

urlpatterns = [

    # AUTH
    path("signup/", views.signup_api),
    path("login/", views.login_api),

    # HOME
    path("homepage/", views.homepage_api),

    # ACTIVITIES
    path("activities/", views.activities_api),

    # BOOKINGS
    path("bookings/<int:user_id>/", views.user_bookings_api),
    path("bookings/create/", views.create_booking_api),

    # PAYMENT
    path("payment/", views.payment_api),

    # REVIEW
    path("review/", views.review_api),

    # PROFILE
    path("profile/<int:user_id>/", views.profile_update_api),

    # NOTIFICATIONS
    path("notifications/<int:user_id>/", views.notifications_api),
]