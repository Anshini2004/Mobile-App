from django.urls import path
from .views import process_payment

urlpatterns = [
    path('payment/', process_payment),
]