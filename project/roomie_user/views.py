# views.py
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import CustomUser,AddressHistory
from .serializers import CustomUserSerializer
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

class CustomUserListView(generics.ListCreateAPIView):
    """
    List all CustomUsers or create a new CustomUser.
    """
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """
        Perform the creation of a new CustomUser.
        You can modify this if you need additional logic before creation.
        """
        serializer.save()


class CustomUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a CustomUser instance.
    """
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Override this to retrieve the user profile of the logged-in user.
        """
        return get_object_or_404(CustomUser, user=self.request.user)

class CustomUserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            custom_user = CustomUser.objects.get(user=request.user)
            # Get the current address (the one with no end_date in AddressHistory)
            current_address = AddressHistory.objects.filter(user=custom_user, end_date__isnull=True).first()
            # Get the address history
            address_history = AddressHistory.objects.filter(user=custom_user).order_by('-start_date')
            
            # Create the response data
            response_data = {
                "id": custom_user.id,
                "user": custom_user.user.id,
                "user_rating_in_app": custom_user.user_rating_in_app,
                "phone_number": custom_user.phone_number,
                "first_name": custom_user.first_name,
                "last_name": custom_user.last_name,
                "email": custom_user.email,
                "has_address": custom_user.has_address,
                "current_address": current_address.address.full_address() if current_address else None,
                "address_history": [
                    {
                        "address": history.address.full_address() if history.address else None,
                        "start_date": history.start_date,
                        "end_date": history.end_date,
                    }
                    for history in address_history
                ],
            }
            return Response(response_data)
        except CustomUser.DoesNotExist:
            return Response({"detail": "Profile not found."}, status=404)


