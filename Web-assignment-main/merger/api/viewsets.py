# merger/api/viewsets.py
from rest_framework import viewsets, permissions
from merger.models import User, Activity
from .serializers import UserSerializer, ActivitySerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]  # or custom, this is what prevents for example a POST to the API.

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """
    Returns data of the currently authenticated user.
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

class ActivityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]