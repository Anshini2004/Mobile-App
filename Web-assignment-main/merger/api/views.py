from django.contrib.auth import authenticate
from rest_framework import permissions, status, viewsets
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from collections import defaultdict
from merger.models import Activity
from django.db.models import Avg, Q
from .serializers import RegisterSerializer, UserSerializer, ActivityCatalogueSerializer


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=["post"], url_path="register")
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "message": "Account created successfully.",
            },
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
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
        url_path="me",
    )
    def me(self, request):
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)

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
        
        
class ActivityViewSet(ViewSet):
    def list(self, request):
        activities = (
            Activity.objects
            .prefetch_related("images")
            .annotate(
                average_rating=Avg(
                    "bookings__review__rating",
                    filter=Q(bookings__review__is_deleted=False)
                )
            )
            .order_by("activity_type", "name")
        )

        serializer = ActivityCatalogueSerializer(
            activities,
            many=True,
            context={"request": request}
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