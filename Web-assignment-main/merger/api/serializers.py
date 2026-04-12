from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from merger.models import Activity, ActivityImage, BookingReview
from django.db.models import Avg

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "phone_number",
            "email",
            "username",
            "password",
            "confirm_password",
        ]
        extra_kwargs = {
            "password": {"write_only": True, "min_length": 8},
            "email": {"required": True},
            "username": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
        }

    def validate_email(self, value):
        value = value.strip().lower()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    def validate_username(self, value):
        value = value.strip()
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def validate_phone_number(self, value):
        value = value.strip()
        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain digits only.")
        if len(value) < 8:
            raise serializers.ValidationError("Phone number must be at least 8 digits.")
        return value

    def validate(self, attrs):
        password = attrs.get("password")
        confirm_password = attrs.pop("confirm_password", None)

        if password != confirm_password:
            raise serializers.ValidationError({
                "confirm_password": ["Passwords do not match."]
            })

        temp_user = User(
            email=attrs.get("email"),
            username=attrs.get("username"),
            first_name=attrs.get("first_name"),
            last_name=attrs.get("last_name"),
        )
        validate_password(password, temp_user)
        return attrs

    def create(self, validated_data):
        phone_number = validated_data.pop("phone_number")
        password = validated_data.pop("password")

        user = User.objects.create_user(
            password=password,
            phone=phone_number,
            **validated_data,
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(source="phone", read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "full_name",
            "phone_number",
            "total_bookings",
            "total_spent",
        ]

    def get_full_name(self, obj):
        return obj.get_full_name().strip() or obj.username or obj.email
    

class ActivityImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ActivityImage
        fields = ["image_url"]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class ActivityCatalogueSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Activity
        fields = [
            "id",
            "name",
            "activity_type",
            "description",
            "base_price",
            "location",
            "duration",
            "max_participants",
            "images",
            "average_rating",
        ]

    def get_images(self, obj):
        request = self.context.get("request")
        return [
            request.build_absolute_uri(img.image.url)
            for img in obj.images.all()
            if img.image
        ]

    def get_average_rating(self, obj):
        avg_rating = getattr(obj, "average_rating", None)
        return round(avg_rating, 1) if avg_rating is not None else None