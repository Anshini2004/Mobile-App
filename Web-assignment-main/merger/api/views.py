# =========================================================
# IMPORTS
# =========================================================

# Django
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import make_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.utils import timezone

# DRF
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

# Models
from merger.models import Activity, Booking, Payment
from ..models import User, BookingReview, Notification

# Serializers
from .serializers import (
    UserSerializer,
    ActivitySerializer,
    ActivityDetailSerializer,
    BookingSerializer,
    BookingCreateSerializer,
    PaymentSerializer,
    BookingReviewSerializer,
    NotificationSerializer,
)

User = get_user_model()


# =========================================================
# AUTH APIs
# =========================================================

@csrf_exempt
def signup_api(request):
    if request.method == "POST":
        data = json.loads(request.body)

        try:
            validate_email(data.get("email"))
        except ValidationError:
            return JsonResponse({"error": "Invalid email"}, status=400)

        if User.objects.filter(email=data.get("email")).exists():
            return JsonResponse({"error": "Email already exists"}, status=400)

        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            return JsonResponse({"message": "User created", "user_id": user.id})

        return JsonResponse(serializer.errors, status=400)


@csrf_exempt
def login_api(request):
    if request.method == "POST":
        data = json.loads(request.body)

        user = authenticate(
            request,
            username=data.get("email"),
            password=data.get("password")
        )

        if user:
            return JsonResponse({
                "message": "Login successful",
                "user_id": user.id
            })

        return JsonResponse({"error": "Invalid credentials"}, status=400)


# =========================================================
# ACTIVITIES (FUNCTION-BASED)
# =========================================================

def activities_api(request):
    activities = Activity.objects.all()
    serializer = ActivitySerializer(activities, many=True)
    return JsonResponse(serializer.data, safe=False)


# =========================================================
# BOOKINGS (FUNCTION-BASED)
# =========================================================

def user_bookings_api(request, user_id):
    bookings = Booking.objects.filter(customer_id=user_id)
    serializer = BookingSerializer(bookings, many=True)
    return JsonResponse(serializer.data, safe=False)


@csrf_exempt
def create_booking_api(request):
    if request.method == "POST":
        data = json.loads(request.body)

        serializer = BookingSerializer(data=data)
        if serializer.is_valid():
            booking = serializer.save()
            return JsonResponse({
                "message": "Booking created",
                "booking_id": booking.id
            })

        return JsonResponse(serializer.errors, status=400)


@csrf_exempt
def cancel_booking_api(request, booking_id):
    if request.method == "PATCH":
        try:
            booking = Booking.objects.get(id=booking_id)

            if booking.status != "CONFIRMED":
                return JsonResponse(
                    {"error": "Only confirmed bookings can be cancelled"},
                    status=400
                )

            booking.status = "CANCELLED"
            booking.save()

            return JsonResponse({"message": "Booking cancelled", "id": booking.id})

        except Booking.DoesNotExist:
            return JsonResponse({"error": "Booking not found"}, status=404)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


# =========================================================
# PAYMENT (FUNCTION-BASED)
# =========================================================

@csrf_exempt
def payment_api(request):
    if request.method == "POST":
        data = json.loads(request.body)

        try:
            booking = Booking.objects.get(id=data.get("booking"))

            payment = Payment.objects.create(
                booking=booking,
                amount=booking.price_total,
                status="PAID",
                paid_at=timezone.now()
            )

            booking.status = "CONFIRMED"
            booking.save()

            serializer = PaymentSerializer(payment)
            return JsonResponse(serializer.data)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


# =========================================================
# REVIEWS
# =========================================================

@csrf_exempt
def review_api(request):
    if request.method == "POST":
        data = json.loads(request.body)

        serializer = BookingReviewSerializer(data=data)
        if serializer.is_valid():
            review = serializer.save()
            return JsonResponse({
                "message": "Review saved",
                "id": review.id
            })

        return JsonResponse(serializer.errors, status=400)


# =========================================================
# PROFILE
# =========================================================

@csrf_exempt
def profile_update_api(request, user_id):
    if request.method == "POST":
        data = json.loads(request.body)

        user = User.objects.get(id=user_id)

        serializer = UserSerializer(user, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({"message": "Profile updated"})

        return JsonResponse(serializer.errors, status=400)


# =========================================================
# NOTIFICATIONS
# =========================================================

def notifications_api(request, user_id):
    notes = Notification.objects.filter(user_id=user_id)
    serializer = NotificationSerializer(notes, many=True)
    return JsonResponse(serializer.data, safe=False)


# =========================================================
# CLASS-BASED VIEWS (NEW API)
# =========================================================

# ── Payment ViewSet ───────────────────────────────────────

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related("booking")
    serializer_class = PaymentSerializer

    def create(self, request, *args, **kwargs):
        try:
            activity_id = request.data.get("activity_id")
            date        = request.data.get("booking_date")
            num_people  = request.data.get("num_people")

            if not activity_id:
                return Response({"error": "activity_id is required"}, status=400)

            if not date:
                return Response({"error": "booking_date is required"}, status=400)

            if not num_people:
                return Response({"error": "num_people is required"}, status=400)

            if request.user.is_authenticated:
                customer = request.user
            else:
                customer = User.objects.filter(is_staff=True).first()
                if not customer:
                    return Response(
                        {"error": "No test user found. Create a superuser first"},
                        status=500,
                    )

            booking = Booking.objects.create(
                activity_id=activity_id,
                date=date,
                group_size=int(num_people),
                customer=customer,
            )

            payment = Payment.objects.create(
                booking=booking,
                amount=booking.price_total,
                method="CARD",
                provider="FletPay",
                status="PAID",
                paid_at=timezone.now(),
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


# ── Activity Views ────────────────────────────────────────

class ActivityListView(generics.ListAPIView):
    queryset = Activity.objects.prefetch_related("images", "highlights").all()
    serializer_class = ActivitySerializer
    permission_classes = [permissions.AllowAny]

    def get_serializer_context(self):
        return {"request": self.request}


class ActivityDetailView(generics.RetrieveAPIView):
    queryset = Activity.objects.prefetch_related(
        "images", "highlights", "bookings__review"
    ).all()
    serializer_class = ActivityDetailSerializer
    permission_classes = [permissions.AllowAny]

    def get_serializer_context(self):
        return {"request": self.request}


# ── Booking Create ───────────────────────────────────────

class BookingCreateView(generics.CreateAPIView):
    serializer_class = BookingCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        return {"request": self.request}

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
                "price_total": str(booking.price_total),
                "status":      booking.status,
            },
            status=status.HTTP_201_CREATED,
        )