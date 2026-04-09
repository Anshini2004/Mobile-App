from rest_framework import serializers
from django.db.models import Avg

from merger.models import Activity, ActivityImage, ActivityHighlight, Booking, BookingReview,Payment


# ── Activity Image ────────────────────────────────────────────────────────────

class ActivityImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model  = ActivityImage
        fields = ["image_url"]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


# ── Activity Highlight ────────────────────────────────────────────────────────

class ActivityHighlightSerializer(serializers.ModelSerializer):
    icon_image_url = serializers.SerializerMethodField()

    class Meta:
        model  = ActivityHighlight
        fields = ["icon_title", "icon_description", "icon_image_url"]

    def get_icon_image_url(self, obj):
        request = self.context.get("request")
        if obj.icon_image and request:
            return request.build_absolute_uri(obj.icon_image.url)
        return None


# ── Reviews ───────────────────────────────────────────────────────────────────

class BookingReviewSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    class Meta:
        model  = BookingReview
        fields = ["rating", "comment", "author", "created_at"]

    def get_author(self, obj):
        # BookingReview has no direct customer field —
        # access it through the related booking
        customer = obj.booking.customer
        return customer.get_full_name() or customer.email


# ── Activity List (lightweight — for browse/home screens) ────────────────────

class ActivityListSerializer(serializers.ModelSerializer):
    images     = ActivityImageSerializer(many=True, read_only=True)
    avg_rating = serializers.SerializerMethodField()

    class Meta:
        model  = Activity
        fields = [
            "id", "name", "location", "activity_type",
            "base_price", "duration", "max_participants",
            "avg_rating", "images",
        ]

    def get_avg_rating(self, obj):
        result = BookingReview.objects.filter(
            booking__activity=obj, is_deleted=False
        ).aggregate(avg=Avg("rating"))
        avg = result["avg"]
        return round(avg, 1) if avg else None


# ── Activity Detail (full data for the detail screen) ────────────────────────

class ActivityDetailSerializer(serializers.ModelSerializer):
    images       = ActivityImageSerializer(many=True, read_only=True)
    highlights   = ActivityHighlightSerializer(many=True, read_only=True)
    avg_rating   = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    reviews      = serializers.SerializerMethodField()

    class Meta:
        model  = Activity
        fields = [
            "id", "name", "location", "activity_type",
            "base_price", "duration", "max_participants",
            "description", "activity_rules", "safety_equipment",
            "cancellation_policy",
            "avg_rating", "review_count",
            "images", "highlights", "reviews",
        ]

    def get_avg_rating(self, obj):
        result = BookingReview.objects.filter(
            booking__activity=obj, is_deleted=False
        ).aggregate(avg=Avg("rating"))
        avg = result["avg"]
        return round(avg, 1) if avg else None

    def get_review_count(self, obj):
        return BookingReview.objects.filter(
            booking__activity=obj, is_deleted=False
        ).count()

    def get_reviews(self, obj):
        reviews = BookingReview.objects.filter(
            booking__activity=obj, is_deleted=False
        ).select_related("booking__customer")   # ← correct select_related path
        return BookingReviewSerializer(reviews, many=True, context=self.context).data


# ── Payment ───────────────────────────────────────────────────────────────────

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = ["status", "paid_at"]


# ── Booking Create ────────────────────────────────────────────────────────────

class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Booking
        fields = ["activity", "date", "group_size"]

    def create(self, validated_data):
        request = self.context["request"]
        return Booking.objects.create(
            customer=request.user,
            **validated_data,
        )