# Django
from collections import defaultdict
from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone
from django.db.models import Avg, Q

# DRF
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework_simplejwt.tokens import RefreshToken

# Models
from merger.models import Activity, Booking, Payment
from ..models import BookingReview, Notification

# Serializers
from .serializers import (
    UserSerializer,
    NearMeActivitySerializer,
    ActivitySerializer,
    ActivityDetailSerializer,
    BookingSerializer,
    BookingCreateSerializer,
    PaymentSerializer,
    BookingReviewSerializer,
    NotificationSerializer,
    RegisterSerializer,
    ActivityCatalogueSerializer,
)

User = get_user_model()


# ── Helpers ───────────────────────────────────────────────

def activity_has_active_booking(activity_id, booking_date):
    return (
        Booking.objects
        .filter(activity_id=activity_id, date=booking_date)
        .exclude(status=Booking.Status.CANCELLED)
        .exists()
    )


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


# ── Bookings ──────────────────────────────────────────────


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def user_bookings_api(request, user_id=None):

    if request.method == "GET":
        bookings = Booking.objects.filter(customer=request.user)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

    elif request.method == "PATCH":
        booking_id = request.data.get("id")

        if not booking_id:
            return Response(
                {"error": "booking_id is required in request body"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            booking = Booking.objects.get(
                id=booking_id,
                customer=request.user
            )

            if booking.status != Booking.Status.CONFIRMED:
                return Response(
                    {"error": "Only confirmed bookings can be cancelled"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            booking.status = Booking.Status.CANCELLED
            booking.save()

            return Response(
                {
                    "message": "Booking cancelled successfully",
                    "booking_id": booking.id,
                    "status": booking.status,
                },
                status=status.HTTP_200_OK,
            )

        except Booking.DoesNotExist:
            return Response(
                {"error": "Booking not found"},
                status=status.HTTP_404_NOT_FOUND,
            )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def booking_detail_api(request, pk):
    """
    Retrieve booking details by booking ID.
    Only the owner of the booking can view it.
    
    GET /bookings/<int:pk>/ -> Get booking details
    """
    try:
        booking = Booking.objects.get(id=pk, customer=request.user)
        serializer = BookingSerializer(booking)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Booking.DoesNotExist:
        return Response(
            {"error": "Booking not found or you don't have permission to view it"},
            status=status.HTTP_404_NOT_FOUND,
        )


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
                "booking_id": booking.pk,
                "activity": booking.activity.name,
                "date": str(booking.date),
                "group_size": booking.group_size,
                "price_total": str(booking.price_total),
                "status": booking.status,
            },
            status=status.HTTP_201_CREATED,
        )

# ── Payments ──────────────────────────────────────────────

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related("booking", "booking__customer")
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(booking__customer=self.request.user)

    def create(self, request, *args, **kwargs):
        try:
            activity_id = request.data.get("activity_id")
            date = request.data.get("booking_date")
            num_people = request.data.get("num_people")

            if not activity_id:
                return Response({"error": "activity_id is required"}, status=400)

            if not date:
                return Response({"error": "booking_date is required"}, status=400)

            if not num_people:
                return Response({"error": "num_people is required"}, status=400)

            if activity_has_active_booking(activity_id, date):
                return Response(
                    {"error": "This activity is already booked for the selected date."},
                    status=400,
                )

            booking = Booking.objects.create(
                activity_id=activity_id,
                date=date,
                group_size=int(num_people),
                customer=request.user,
            )

            payment = Payment.objects.create(
                booking=booking,
                amount=booking.price_total,
                method="CARD",
                provider="FletPay",
                status="PAID",
                paid_at=timezone.now(),
            )

            booking.status = Booking.Status.CONFIRMED
            booking.save()

            return Response(
                {
                    "status": "success",
                    "booking_id": booking.id,
                    "payment_id": payment.id,
                    "customer": request.user.email,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ── Activities ────────────────────────────────────────────

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


class NearMeActivityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = NearMeActivitySerializer
    permission_classes = [permissions.AllowAny]


class ActivityViewSet(ViewSet):
    permission_classes = [permissions.AllowAny]

    def list(self, request):
        activities = (
            Activity.objects
            .prefetch_related("images")
            .annotate(
                average_rating=Avg(
                    "bookings__review__rating",
                    filter=Q(bookings__review__is_deleted=False),
                )
            )
            .order_by("activity_type", "name")
        )

        serializer = ActivityCatalogueSerializer(
            activities,
            many=True,
            context={"request": request},
        )

        grouped = defaultdict(list)
        for item in serializer.data:
            grouped[item["activity_type"]].append(item)

        result = [
            {
                "activity_type": activity_type,
                "activities": items,
            }
            for activity_type, items in grouped.items()
        ]

        return Response(result)


@api_view(["GET", "POST", "PATCH", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def activity_management_api(request, activity_id=None):

    if not request.user.is_staff:
        return Response(
            {"error": "Only staff users can access this endpoint"},
            status=status.HTTP_403_FORBIDDEN,
        )

    if request.method == "GET":
        aid = activity_id or request.data.get("activity_id")

        if aid:
            # Get specific activity
            try:
                activity = Activity.objects.prefetch_related(
                    "images",
                    "highlights"
                ).get(id=aid)

                serializer = ActivitySerializer(
                    activity,
                    context={"request": request},
                )
                return Response(serializer.data, status=status.HTTP_200_OK)

            except Activity.DoesNotExist:
                return Response(
                    {"error": "Activity not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            # Get all activities
            activities = Activity.objects.prefetch_related(
                "images",
                "highlights"
            ).all()

            serializer = ActivitySerializer(
                activities,
                many=True,
                context={"request": request},
            )
            return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == "POST":
        serializer = ActivitySerializer(
            data=request.data,
            context={"request": request},
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    elif request.method == "PATCH":
        aid = activity_id or request.data.get("activity_id")

        if not aid:
            return Response(
                {"error": "activity_id is required in request body"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            activity = Activity.objects.get(id=aid)

            serializer = ActivitySerializer(
                activity,
                data=request.data,
                partial=True,
                context={"request": request},
            )

            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_200_OK,
                )

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Activity.DoesNotExist:
            return Response(
                {"error": "Activity not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    elif request.method == "PUT":
        aid = activity_id or request.data.get("activity_id")

        if not aid:
            return Response(
                {"error": "activity_id is required in request body"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            activity = Activity.objects.get(id=aid)

            serializer = ActivitySerializer(
                activity,
                data=request.data,
                partial=False,
                context={"request": request},
            )

            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_200_OK,
                )

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Activity.DoesNotExist:
            return Response(
                {"error": "Activity not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    elif request.method == "DELETE":
        aid = activity_id or request.data.get("activity_id")

        if not aid:
            return Response(
                {"error": "activity_id is required in request body"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            activity = Activity.objects.get(id=aid)
            activity.delete()

            return Response(
                {"message": "Activity deleted successfully"},
                status=status.HTTP_200_OK,
            )

        except Activity.DoesNotExist:
            return Response(
                {"error": "Activity not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

# ── Users / Auth ──────────────────────────────────────────

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def current_user(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=["post"], url_path="register")
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "Account created successfully."},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"], url_path="login")
    def login(self, request):
        email = (request.data.get("email") or "").strip().lower()
        password = request.data.get("password") or ""

        if not email:
            return Response(
                {"email": ["Email is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not password:
            return Response(
                {"password": ["Password is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request=request, username=email, password=password)

        if user is None:
            return Response(
                {"non_field_errors": ["Invalid email or password."]},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return Response(
                {"non_field_errors": ["This account is inactive."]},
                status=status.HTTP_403_FORBIDDEN,
            )

        tokens = get_tokens_for_user(user)

        return Response(
            {
                "message": "Login successful.",
                "user": UserSerializer(user).data,
                "tokens": tokens,
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["get", "patch"],
        permission_classes=[permissions.IsAuthenticated],
        url_path="me",
    )
    def me(self, request):
        if request.method == "GET":
            serializer = UserSerializer(request.user)
            return Response(serializer.data)

        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        url_path="logout",
    )
    def logout(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"refresh": ["Refresh token is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"message": "Logout successful."},
                status=status.HTTP_205_RESET_CONTENT,
            )
        except Exception:
            return Response(
                {"detail": "Invalid refresh token."},
                status=status.HTTP_400_BAD_REQUEST,
            )


# ── Reviews ───────────────────────────────────────────────

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def review_api(request):
    serializer = BookingReviewSerializer(data=request.data)

    if serializer.is_valid():
        review = serializer.save()
        return Response(
            {
                "message": "Review saved",
                "id": review.id,
            },
            status=status.HTTP_201_CREATED,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ── Notifications ─────────────────────────────────────────

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def notifications_api(request, user_id):
    """
    Old URL-compatible endpoint:
    /notifications/<int:user_id>/

    user_id is ignored on purpose.
    JWT request.user is used instead.
    """
    notes = Notification.objects.filter(user=request.user)
    serializer = NotificationSerializer(notes, many=True)
    return Response(serializer.data)