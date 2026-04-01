from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone

from ..models import Activity, Booking, Payment, User
from .serializers import PaymentAPISerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def process_payment(request):
    serializer = PaymentAPISerializer(data=request.data)

    # ❌ Invalid input
    if not serializer.is_valid():
        return Response({"errors": serializer.errors}, status=400)

    data = serializer.validated_data

    try:
        # ✅ Get activity
        activity = get_object_or_404(Activity, id=data['activity_id'])

        # ✅ Get a default user (TEMP solution)
        default_user = User.objects.first()

        if not default_user:
            return Response({"error": "No users found in database"}, status=400)

        # ✅ Create booking (price auto calculated in model)
        booking = Booking.objects.create(
            customer=default_user,  # 🔥 FIXED HERE
            activity=activity,
            date=data['booking_date'],
            group_size=data['num_people'],
            status=Booking.Status.CONFIRMED
        )

        # ✅ Create payment
        payment = Payment.objects.create(
            booking=booking,
            amount=booking.price_total,
            method=Payment.Method.CARD,
            status=Payment.Status.PAID,
            provider="Mobile App",
            paid_at=timezone.now()
        )

        # ✅ Success response
        return Response({
            "status": "success",
            "booking_id": booking.id,
            "amount": booking.price_total
        })

    except Exception as e:
        return Response({"error": str(e)}, status=500)