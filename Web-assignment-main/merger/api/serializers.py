from rest_framework import serializers

class PaymentAPISerializer(serializers.Serializer):
    activity_id = serializers.IntegerField()
    booking_date = serializers.DateField()
    num_people = serializers.IntegerField()

    card_number = serializers.CharField()
    card_name = serializers.CharField()
    expiry_date = serializers.CharField()
    cvv = serializers.CharField()