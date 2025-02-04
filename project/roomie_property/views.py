# views.py

from rest_framework import viewsets
from rest_framework.views import APIView
from .models import Property
from .serializers import PropertySerializer,OwnerPropertiesSerializer
from rest_framework.permissions import IsAuthenticated

class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer

# APIView for Owner's Dashboard
class OwnerDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get the logged-in user (owner)
        owner = request.user  
        
        # Fetch the properties owned by the logged-in user
        owner_properties = Property.objects.filter(owner=owner)  # Query properties owned by the logged-in user
        
        # Serialize the properties data
        serializer = OwnerPropertiesSerializer(owner_properties, many=True)
        
        # Return the serialized data
        return Response(serializer.data)