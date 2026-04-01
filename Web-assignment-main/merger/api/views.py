from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password, check_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Avg, Q
import json

from ..models import (
    User, Activity, Booking, Payment,
    BookingReview, Notification
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

        user = User.objects.create(
            email=data.get("email"),
            username=data.get("email"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            password=make_password(data.get("password"))
        )

        return JsonResponse({"message": "User created", "user_id": user.id})


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
# HOMEPAGE DATA
# ---------------------------

def homepage_api(request):
    def get_stats(activity_type):
        reviews = BookingReview.objects.filter(
            booking__activity__activity_type=activity_type,
            is_deleted=False
        )
        return {
            "avg": round(reviews.aggregate(avg=Avg('rating'))['avg'] or 0, 1),
            "total": reviews.count()
        }

    data = {
        "catamaran": get_stats("Catamaran"),
        "scuba": get_stats("Scuba diving"),
        "dolphin": get_stats("Dolphin watching"),
        "ski": get_stats("Water ski"),
        "boat": get_stats("Speed boat"),
    }

    return JsonResponse(data)


# ---------------------------
# ACTIVITIES
# ---------------------------

def activities_api(request):
    activities = Activity.objects.all()

    data = []
    for act in activities:
        data.append({
            "id": act.id,
            "name": act.name,
            "type": act.activity_type,
            "price": act.base_price,
            "location": act.location
        })

    return JsonResponse({"activities": data})


# ---------------------------
# BOOKINGS
# ---------------------------

def user_bookings_api(request, user_id):
    bookings = Booking.objects.filter(customer_id=user_id)

    data = []
    for b in bookings:
        data.append({
            "id": b.id,
            "activity": b.activity.name,
            "date": b.date,
            "status": b.status,
            "price": b.price_total
        })

    return JsonResponse({"bookings": data})


@csrf_exempt
def create_booking_api(request):
    if request.method == "POST":
        data = json.loads(request.body)

        try:
            activity = Activity.objects.get(id=data.get("activity_id"))

            booking = Booking.objects.create(
                customer_id=data.get("user_id"),
                activity=activity,
                date=data.get("date"),
                group_size=data.get("group_size")
            )

            return JsonResponse({
                "message": "Booking created",
                "booking_id": booking.id
            })

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
            booking = Booking.objects.get(id=data.get("booking_id"))

            Payment.objects.create(
                booking=booking,
                amount=booking.price_total,
                status="PAID",
                paid_at=timezone.now()
            )

            booking.status = "CONFIRMED"
            booking.save()

            return JsonResponse({"message": "Payment successful"})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


# ---------------------------
# REVIEWS
# ---------------------------

@csrf_exempt
def review_api(request):
    if request.method == "POST":
        data = json.loads(request.body)

        try:
            booking = Booking.objects.get(id=data.get("booking_id"))

            review, created = BookingReview.objects.update_or_create(
                booking=booking,
                defaults={
                    "customer_id": data.get("user_id"),
                    "rating": data.get("rating"),
                    "comment": data.get("comment")
                }
            )

            return JsonResponse({
                "message": "Review saved",
                "created": created
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


# ---------------------------
# PROFILE
# ---------------------------

@csrf_exempt
def profile_update_api(request, user_id):
    if request.method == "POST":
        data = json.loads(request.body)

        user = User.objects.get(id=user_id)

        if "email" in data:
            try:
                validate_email(data["email"])
                user.email = data["email"]
            except ValidationError:
                return JsonResponse({"error": "Invalid email"}, status=400)

        if "password" in data:
            user.password = make_password(data["password"])

        user.first_name = data.get("first_name", user.first_name)
        user.last_name = data.get("last_name", user.last_name)

        user.save()

        return JsonResponse({"message": "Profile updated"})


# ---------------------------
# NOTIFICATIONS
# ---------------------------

def notifications_api(request, user_id):
    notes = Notification.objects.filter(user_id=user_id)

    data = []
    for n in notes:
        parts = n.message.split("|||")
        data.append({
            "title": n.title,
            "message": parts[0],
            "details": parts[1] if len(parts) > 1 else "",
            "date": n.created_at
        })

    return JsonResponse({"notifications": data})




