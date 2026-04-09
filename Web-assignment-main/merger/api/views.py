# ── All imports at the top (no more duplicate blocks) ────────────────────────
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from django.shortcuts import get_object_or_404
from django.utils import timezone

from merger.models import Activity, Booking, Payment
from django.contrib.auth import get_user_model

from .serializers import (
    PaymentSerializer,
    ActivityListSerializer,
    ActivityDetailSerializer,
    BookingCreateSerializer,
)

User = get_user_model()


# ── Payment ───────────────────────────────────────────────────────────────────

from django.utils.timezone import now
from rest_framework import viewsets
from rest_framework.response import Response
from merger.models import Booking, Payment
from .serializers import PaymentSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related("booking")
    serializer_class = PaymentSerializer

    def create(self, request, *args, **kwargs):
        try:
            activity_id = request.data.get("activity_id")
            date        = request.data.get("booking_date")
            num_people  = request.data.get("num_people")

            # ── Validation ───────────────────────────────────────────────────
            if not activity_id:
                return Response({"error": "activity_id is required"}, status=400)

            if not date:
                return Response({"error": "booking_date is required"}, status=400)

            if not num_people:
                return Response({"error": "num_people is required"}, status=400)

            # ── Customer ─────────────────────────────────────────────────────
            # TODO: replace this with request.user once login is integrated
            if request.user.is_authenticated:
                customer = request.user
            else:
                # Temporary fallback for testing without login
                # Uses the first superuser/staff account in the DB
                customer = User.objects.filter(is_staff=True).first()
                if not customer:
                    return Response(
                        {"error": "No test user found. Create a superuser first: python manage.py createsuperuser"},
                        status=500,
                    )

            # ── Create Booking ───────────────────────────────────────────────
            booking = Booking.objects.create(
                activity_id=activity_id,
                date=date,
                group_size=int(num_people),
                customer=customer,
            )

            # ── Create Payment ───────────────────────────────────────────────
            payment = Payment.objects.create(
                booking=booking,
                amount=booking.price_total,
                method="CARD",
                provider="FletPay",
                status="PAID",
                paid_at=now(),
            )

            return Response(
                {
                    "status": "success",
                    "booking_id": booking.id,
                    "payment_id": payment.id,
                },
                status=200,
            )

        except Exception as e:
            return Response({"error": str(e)}, status=500)
# ── Activities ────────────────────────────────────────────────────────────────

class ActivityListView(generics.ListAPIView):
    """
    GET /api/activities/
    Returns all activities (lightweight card data).
    """
    queryset           = Activity.objects.prefetch_related("images", "highlights").all()
    serializer_class   = ActivityListSerializer
    permission_classes = [permissions.AllowAny]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx


class ActivityDetailView(generics.RetrieveAPIView):
    """
    GET /api/activities/<pk>/
    Returns full activity detail including images, highlights and reviews.
    """
    queryset = Activity.objects.prefetch_related(
        "images", "highlights", "bookings__review"
    ).all()
    serializer_class   = ActivityDetailSerializer
    permission_classes = [permissions.AllowAny]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx


# ── Bookings ──────────────────────────────────────────────────────────────────

class BookingCreateView(generics.CreateAPIView):
    """
    POST /api/bookings/
    Creates a booking for the authenticated user.
    Body: { "activity": <id>, "date": "YYYY-MM-DD", "group_size": <int> }
    """
    serializer_class   = BookingCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()
        return Response(
            {
                "booking_id":  booking.pk,
                "activity":    booking.activity.name,
                "date":        str(booking.date),
                "group_size":  booking.group_size,
                "price_total": str(booking.price_total),  # Decimal → string
                "status":      booking.status,
            },
            status=status.HTTP_201_CREATED,
        )