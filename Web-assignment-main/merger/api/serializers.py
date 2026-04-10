from rest_framework import serializers
from merger.models import User, Activity

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'username',
            'email',
            'phone',
            'total_bookings',
            'total_spent',
            'password',
        ]

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance


class ActivitySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Activity
        fields = [
            'id',
            'name',
            'location',
            'activity_type',
            'description',
            'image'
        ]

    def get_image(self, obj):
        request = self.context.get('request')
        first_image = obj.images.first()

        if first_image and first_image.image:
            if request:
                return request.build_absolute_uri(first_image.image.url)
            return first_image.image.url

        return None