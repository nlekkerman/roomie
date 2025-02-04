# views.py
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import CustomUser,AddressHistory
from .serializers import CustomUserSerializer
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

class CustomUserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Get the custom user instance for the currently authenticated user
            custom_user = CustomUser.objects.get(user=request.user)
            
            # Get the current address (the one with no end_date in AddressHistory)
            current_address = AddressHistory.objects.filter(
                user=custom_user, 
                end_date__isnull=True
            ).first()
            
            # Get the address history
            address_history = AddressHistory.objects.filter(user=custom_user).order_by('-start_date')
            
            # Create the response data
            response_data = {
                "id": custom_user.id,
                "user": custom_user.user.id,
                "profile_image": custom_user.profile_image.url if custom_user.profile_image else None,
                "user_rating_in_app": custom_user.user_rating_in_app,
                "phone_number": custom_user.phone_number,
                "first_name": custom_user.first_name,
                "last_name": custom_user.last_name,
                "email": custom_user.email,
                "has_address": custom_user.has_address,
                "current_address": {
                    "full_address": current_address.address.full_address() if current_address and current_address.address else None,
                    "property_id": current_address.address.id if current_address and current_address.address else None  # Add property ID
                },
                "address_history": [
                    {
                        "address": history.address.full_address() if history.address else None,
                        "property_id": history.address.id if history.address else None,  # Include property ID in address history
                        "start_date": history.start_date,
                        "end_date": history.end_date,
                    }
                    for history in address_history
                ],
            }
            
            return Response(response_data)
        
        except CustomUser.DoesNotExist:
            return Response({"detail": "Profile not found."}, status=404)