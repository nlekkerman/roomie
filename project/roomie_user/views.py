# views.py
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import CustomUser,AddressHistory
from .serializers import CustomUserSerializer
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError

class CustomUserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Try to get the CustomUser instance based on the authenticated user
        try:
            custom_user = CustomUser.objects.get(user=request.user)
            
            # Debugging: Print custom_user properties
            print("Fetched Custom User:", custom_user)
            
            # Fetch the current address
            current_address = AddressHistory.objects.filter(
                user=custom_user, 
                end_date__isnull=True
            ).first()

            # Debugging: Print the current address if available
            if current_address and current_address.address:
                print("Current Address:", current_address.address.full_address())
            else:
                print("No current address found.")

            # Fetch address history
            address_history = AddressHistory.objects.filter(user=custom_user, end_date__isnull=False).order_by('-start_date')

          
            # Prepare response data
            response_data = {
                "status": "custom_user",  # Indicating it's a custom user
                "id": custom_user.pk,
                "profile_image": custom_user.profile_image.url if custom_user.profile_image else None,
                "user_rating_in_app": custom_user.user_rating_in_app,
                "phone_number": custom_user.phone_number,
                "first_name": custom_user.first_name,
                "last_name": custom_user.last_name,
                "email": custom_user.email,
                # Handle case when current_address or current_address.address is None
                "property_id": current_address.address.id if current_address and current_address.address else None,
                "current_address": current_address.address.full_address() if current_address and current_address.address else None,
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
            # If no custom user is found, return a default response
            return Response(
                {"status": "default_user", "message": "No custom profile found. Please complete your profile."},
                status=200  # Change status to 200 to indicate it's a valid user but missing profile
            )

    def post(self, request):
        try:
            print("POST Request received")
            print("Request Data:", request.data)
            print("Request User:", request.user)

            # Ensure the user is valid
            if not request.user or not request.user.is_authenticated:
                return Response({"status": "error", "message": "User not authenticated."}, status=400)

            # Log the user ID for debugging
            print(f"Request User ID: {request.user.id}")

            # Check if the user already has an associated CustomUser
            custom_user = CustomUser.objects.filter(user=request.user).first()

            if custom_user:
                # CustomUser already exists, update instead
                print(f"🔄 Updating existing CustomUser with ID: {custom_user.pk}")
                serializer = CustomUserSerializer(custom_user, data=request.data, partial=True, context={'request': request})

                if serializer.is_valid():
                    serializer.save()
                    print(f"✅ CustomUser updated with ID: {custom_user.pk}")
                    return Response(
                        {
                            "status": "success",
                            "message": "Custom user profile updated successfully",
                            "data": serializer.data,
                        },
                        status=200,
                    )
                else:
                    print("❌ Serializer Errors:", serializer.errors)
                    return Response(
                        {"status": "error", "message": "Invalid data", "errors": serializer.errors},
                        status=400,
                    )

            else:
                # CustomUser doesn't exist, create a new one
                print("Creating new CustomUser.")
                custom_user = CustomUser(user=request.user)
                serializer = CustomUserSerializer(custom_user, data=request.data, context={'request': request})

                if serializer.is_valid():
                    serializer.save()
                    print(f"✅ New CustomUser created with ID: {custom_user.pk}")
                    return Response(
                        {
                            "status": "success",
                            "message": "Custom user profile created successfully",
                            "data": serializer.data,
                        },
                        status=201,
                    )
                else:
                    print("❌ Serializer Errors:", serializer.errors)
                    return Response(
                        {"status": "error", "message": "Invalid data", "errors": serializer.errors},
                        status=400,
                    )

        except IntegrityError:
            print("🔥 IntegrityError: CustomUser already exists")
            return Response(
                {"status": "error", "message": "Custom user profile already exists."},
                status=400,
            )

        except Exception as e:
            print("🔥 General Error Occurred:", e)
            return Response(
                {"status": "error", "message": f"An error occurred: {str(e)}"},
                status=500,
            )

class DefaultUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name
        })
        