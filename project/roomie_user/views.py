from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import Profile
from .serializers import ProfileSerializer
from rest_framework.generics import ListAPIView


class ProfileListView(ListAPIView):
    queryset = Profile.objects.all()  # Retrieve all profiles
    serializer_class = ProfileSerializer  # Serialize the profiles

# Create View (already defined)
class ProfileCreateView(generics.CreateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [AllowAny]

# Retrieve View
class ProfileRetrieveView(generics.RetrieveAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [AllowAny]  # Adjust permissions as needed

# Update View
class ProfileUpdateView(generics.UpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [AllowAny]  # Adjust permissions as needed

# Delete View
class ProfileDeleteView(generics.DestroyAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [AllowAny]  # Adjust permissions as needed
