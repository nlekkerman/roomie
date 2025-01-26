# views.py

from rest_framework import viewsets
from .models import Property
from .serializers import PropertySerializer
from rest_framework.permissions import IsAuthenticated

class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [IsAuthenticated]  # Optional: Ensure only authenticated users can access
