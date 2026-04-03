from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from ..models import (
    User, Activity, ActivityImage, ActivityHighlight,
    Booking, Payment, BookingReview, Notification
)

# ---------------------------
# USER SERIALIZER
# ---------------------------

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "id", "email", "first_name", "last_name",
            "phone", "password", "total_bookings", "total_spent"
        ]

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "password" in validated_data:
            instance.password = make_password(validated_data.pop("password"))
        return super().update(instance, validated_data)


# ---------------------------
# ACTIVITY SERIALIZERS
# ---------------------------

class ActivityImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityImage
        fields = ["id", "image"]


class ActivityHighlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityHighlight
        fields = ["id", "icon_title", "icon_description", "icon_image"]


class ActivitySerializer(serializers.ModelSerializer):
    images = ActivityImageSerializer(many=True, read_only=True)
    highlights = ActivityHighlightSerializer(many=True, read_only=True)

    class Meta:
        model = Activity
        fields = [
            "id", "name", "activity_type", "description",
            "base_price", "location", "duration",
            "max_participants",
            "activity_rules", "safety_equipment", "cancellation_policy",
            "map_embed_url", "map_location_description",
            "images", "highlights"
        ]


# ---------------------------
# BOOKING SERIALIZER
# ---------------------------

class BookingSerializer(serializers.ModelSerializer):
    activity_name = serializers.CharField(source="activity.name", read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id", "customer", "activity", "activity_name",
            "date", "group_size", "price_total",
            "status", "created_at"
        ]
        read_only_fields = ["price_total", "status"]


# ---------------------------
# PAYMENT SERIALIZER
# ---------------------------

class PaymentSerializer(serializers.ModelSerializer):
    activity_name = serializers.CharField(source="booking.activity.name", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id", "booking", "amount",
            "method", "status",
            "provider", "paid_at",
            "activity_name"
        ]
        read_only_fields = ["status", "paid_at"]


# ---------------------------
# REVIEW SERIALIZER
# ---------------------------

class BookingReviewSerializer(serializers.ModelSerializer):
    activity_name = serializers.CharField(source="booking.activity.name", read_only=True)
    customer_name = serializers.CharField(source="customer.first_name", read_only=True)

    class Meta:
        model = BookingReview
        fields = [
            "id", "booking", "customer",
            "rating", "comment",
            "created_at",
            "activity_name", "customer_name"
        ]


# ---------------------------
# NOTIFICATION SERIALIZER
# ---------------------------

class NotificationSerializer(serializers.ModelSerializer):
    message_part = serializers.SerializerMethodField()
    details_part = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            "id", "title", "message",
            "message_part", "details_part",
            "type", "created_at"
        ]

    def get_message_part(self, obj):
        return obj.message.split("|||")[0]

    def get_details_part(self, obj):
        parts = obj.message.split("|||")
        return parts[1] if len(parts) > 1 else ""


# ---------------------------
# HOMEPAGE STATS SERIALIZER
# ---------------------------

class ActivityStatsSerializer(serializers.Serializer):
    avg = serializers.FloatField()
    total = serializers.IntegerField()