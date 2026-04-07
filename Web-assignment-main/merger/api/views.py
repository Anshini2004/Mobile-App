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
    PaymentAPISerializer,
    ActivityListSerializer,
    ActivityDetailSerializer,
    BookingCreateSerializer,
)

User = get_user_model()


# ── Payment ───────────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def process_payment(request):
    serializer = PaymentAPISerializer(data=request.data)

    if not serializer.is_valid():
        return Response({"errors": serializer.errors}, status=400)

    data = serializer.validated_data

    try:
        activity = get_object_or_404(Activity, id=data['activity_id'])

        # TEMP: use first user until auth is wired up
        default_user = User.objects.first()
        if not default_user:
            return Response({"error": "No users found in database"}, status=400)

        booking = Booking.objects.create(
            customer=default_user,
            activity=activity,
            date=data['booking_date'],
            group_size=data['num_people'],
            status=Booking.Status.CONFIRMED,
        )

        payment = Payment.objects.create(
            booking=booking,
            amount=booking.price_total,
            method=Payment.Method.CARD,
            status=Payment.Status.PAID,
            provider="Mobile App",
            paid_at=timezone.now(),
        )

        return Response({
            "status":     "success",
            "booking_id": booking.id,
            "amount":     str(booking.price_total),   # Decimal → string for JSON
        })

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