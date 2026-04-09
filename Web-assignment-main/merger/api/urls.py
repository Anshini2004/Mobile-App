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
    path("", include(router.urls)),

    path("activities/", ActivityListView.as_view()),
    path("activities/<int:pk>/", ActivityDetailView.as_view()),
    path("bookings/", BookingCreateView.as_view()),
]