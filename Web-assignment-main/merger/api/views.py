from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils import timezone
import json

from ..models import (
    User, Activity, Booking, Payment,
    BookingReview, Notification
)

from .serializers import (
    UserSerializer,
    ActivitySerializer,
    BookingSerializer,
    PaymentSerializer,
    BookingReviewSerializer,
    NotificationSerializer
)

# ---------------------------
# AUTH APIs
# ---------------------------

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


# ---------------------------
# ACTIVITIES
# ---------------------------

def activities_api(request):
    activities = Activity.objects.all()
    serializer = ActivitySerializer(activities, many=True)
    return JsonResponse(serializer.data, safe=False)


# ---------------------------
# BOOKINGS
# ---------------------------

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


# ---------------------------
# PAYMENT
# ---------------------------

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


# ---------------------------
# REVIEWS
# ---------------------------

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


# ---------------------------
# PROFILE
# ---------------------------

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


# ---------------------------
# NOTIFICATIONS
# ---------------------------

def notifications_api(request, user_id):
    notes = Notification.objects.filter(user_id=user_id)
    serializer = NotificationSerializer(notes, many=True)
    return JsonResponse(serializer.data, safe=False)