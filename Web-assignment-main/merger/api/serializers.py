from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.db.models import Avg

from ..models import (
    User, Activity, ActivityImage, ActivityHighlight,
    Booking, Payment, BookingReview, Notification
)

# ---------------------------
# USER SERIALIZER
# ---------------------------

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required = False)

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
# ACTIVITY IMAGE
# ---------------------------

class ActivityImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ActivityImage
        fields = ["id", "image_url"]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


# ---------------------------
# ACTIVITY HIGHLIGHT
# ---------------------------

class ActivityHighlightSerializer(serializers.ModelSerializer):
    icon_image_url = serializers.SerializerMethodField()

    class Meta:
        model = ActivityHighlight
        fields = ["id", "icon_title", "icon_description", "icon_image_url"]

    def get_icon_image_url(self, obj):
        request = self.context.get("request")
        if obj.icon_image and request:
            return request.build_absolute_uri(obj.icon_image.url)
        return None


# ---------------------------
# ACTIVITY LIST (LIGHT)
# ---------------------------

class ActivitySerializer(serializers.ModelSerializer):
    images = ActivityImageSerializer(many=True, read_only=True)
    avg_rating = serializers.SerializerMethodField()

    class Meta:
        model = Activity
        fields = [
            "id", "name", "location", "activity_type",
            "base_price", "duration", "max_participants",
            "avg_rating", "images","description", "image"
        ]

    def get_avg_rating(self, obj):
        result = BookingReview.objects.filter(
            booking__activity=obj
        ).aggregate(avg=Avg("rating"))
        return round(result["avg"], 1) if result["avg"] else None
    
    def get_image(self, obj):
        request = self.context.get('request')
        first_image = obj.images.first()

        if first_image and first_image.image:
            if request:
                return request.build_absolute_uri(first_image.image.url)
            return first_image.image.url

        return None


# ---------------------------
# ACTIVITY DETAIL
# ---------------------------

class ActivityDetailSerializer(serializers.ModelSerializer):
    images = ActivityImageSerializer(many=True, read_only=True)
    highlights = ActivityHighlightSerializer(many=True, read_only=True)
    avg_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()

    class Meta:
        model = Activity
        fields = [
            "id", "name", "activity_type", "description",
            "base_price", "location", "duration",
            "max_participants",
            "activity_rules", "safety_equipment", "cancellation_policy",
            "map_embed_url", "map_location_description",
            "avg_rating", "review_count",
            "images", "highlights", "reviews"
        ]

    def get_avg_rating(self, obj):
        result = BookingReview.objects.filter(
            booking__activity=obj
        ).aggregate(avg=Avg("rating"))
        return round(result["avg"], 1) if result["avg"] else None

    def get_review_count(self, obj):
        return BookingReview.objects.filter(
            booking__activity=obj
        ).count()

    def get_reviews(self, obj):
        reviews = BookingReview.objects.filter(
            booking__activity=obj
        ).select_related("booking__customer")
        return BookingReviewSerializer(
            reviews, many=True, context=self.context
        ).data


# ---------------------------
# BOOKING
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


class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ["activity", "date", "group_size"]

    def create(self, validated_data):
        request = self.context["request"]
        return Booking.objects.create(
            customer=request.user,
            **validated_data
        )


# ---------------------------
# PAYMENT
# ---------------------------

class PaymentSerializer(serializers.ModelSerializer):
    activity_name = serializers.CharField(
        source="booking.activity.name", read_only=True
    )

    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = ["status", "paid_at"]


# ---------------------------
# REVIEW
# ---------------------------

class BookingReviewSerializer(serializers.ModelSerializer):
    activity_name = serializers.CharField(
        source="booking.activity.name", read_only=True
    )
    customer_name = serializers.SerializerMethodField()

    class Meta:
        model = BookingReview
        fields = [
            "id", "booking", "rating", "comment",
            "created_at", "activity_name", "customer_name"
        ]

    def get_customer_name(self, obj):
        customer = obj.booking.customer
        return customer.get_full_name() or customer.email


# ---------------------------
# NOTIFICATION
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
