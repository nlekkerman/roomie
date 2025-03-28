# views.py

from rest_framework import viewsets, status
from rest_framework.views import APIView
from .models import Property, RoomImage, TenancyRequest
from roomie_user.serializers import CustomUserSerializer
from communication.serializers import NotificationSerializer
from .serializers import PropertySerializer, OwnerPropertiesSerializer, RoomImageSerializer, TenancyRequestSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
import cloudinary.uploader
from roomie_user.models import CustomUser
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile


class PropertyPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 100

class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    parser_classes = [MultiPartParser, FormParser]
    pagination_class = PropertyPagination

    def create(self, request, *args, **kwargs):
        try:
            print(f"Request data received: {request.data}")
            request.data['owner'] = request.user.id  
            if 'folio_number' in request.data:
                print(f"folio_number: {request.data['folio_number']}")
            return super().create(request, *args, **kwargs)
        except Exception as e:
            print(f"Error creating property: {e}")
            return Response({"error": "An error occurred while creating the property."},
                            status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        try:
            property_instance = self.get_object()
            
            if 'delete_image_public_id' in request.data:
                delete_image_public_id = request.data['delete_image_public_id']
                print(f"Attempting to delete image with Cloudinary public ID: {delete_image_public_id}")
                cloudinary.uploader.destroy(delete_image_public_id)  
                room_image = property_instance.room_images.filter(image__contains=delete_image_public_id).first()
                if room_image:
                    room_image.delete()
                    print(f"Deleted image with public ID: {delete_image_public_id} from the database.")
            
            if 'main_image' in request.FILES:
                property_instance.main_image = request.FILES['main_image']
                property_instance.save()
                print(f"Main image updated: {property_instance.main_image.url}")

            if 'room_image' in request.FILES:
                room_images = request.FILES.getlist('room_image')
                print(f"Inside partial_update method. Room images count: {len(room_images)}")

                for img in room_images:
                    print(f"Adding room image: {img.name}")
                    RoomImage.objects.create(
                        property=property_instance,
                        image=img,
                        description='Updated room image'
                    )

                print(f"{len(room_images)} room images added.")

            property_instance.save()
            print("Property instance saved successfully.")
            return Response(PropertySerializer(property_instance).data, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error: {e}")
            return Response({"error": "An error occurred while updating the property."},
                            status=status.HTTP_400_BAD_REQUEST)

class OwnerDashboardView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = PropertyPagination  # Use pagination class

    def get(self, request):
        # ✅ Get the logged-in owner
        owner = request.user
        # ✅ Fetch owned properties
        owner_properties = Property.objects.filter(owner=owner)

        # Apply pagination
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(owner_properties, request)
        
        # Serialize the paginated data
        serializer = PropertySerializer(result_page, many=True)

        # Return the paginated response
        return paginator.get_paginated_response(serializer.data) 

class PropertyCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser]  # To handle file uploads (image files)

    def convert_to_webp(self, image):
        """Convert and resize image to WebP format"""
        img = Image.open(image)

        # Resize if needed (e.g., max 800x800)
        max_size = (800, 800)
        img.thumbnail(max_size)

        # Convert to WebP
        img_io = BytesIO()
        img.save(img_io, format='WEBP', quality=80)

        # Return converted image
        return ContentFile(img_io.getvalue(), name=f"{image.name.split('.')[0]}.webp")

    def post(self, request, *args, **kwargs):
        # Copy request data
        property_data = request.data.copy()

        # Retrieve files (images)
        main_image = request.FILES.get('main_image')
        room_images = request.FILES.getlist('room_images')

        # Convert main image to WebP
        if main_image:
            main_image = self.convert_to_webp(main_image)

        # Create Property instance
        property = Property.objects.create(
            street=property_data['street'],
            house_number=property_data['house_number'],
            town=property_data['town'],
            county=property_data['county'],
            country=property_data['country'],
            property_rating=property_data['property_rating'],
            room_capacity=property_data['room_capacity'],
            people_capacity=property_data['people_capacity'],
            rent_amount=property_data['rent_amount'],
            deposit_amount=property_data['deposit_amount'],
            folio_number=property_data['folio_number'],
            air_code=property_data.get('air_code'),
            description=property_data.get('description'),
            main_image=main_image,
            owner=request.user
        )

        # Convert and save room images
        for img in room_images:
            converted_img = self.convert_to_webp(img)
            RoomImage.objects.create(
                property=property,
                image=converted_img,
                description='Room image description'
            )

        # Return response
        return Response(PropertySerializer(property).data, status=status.HTTP_201_CREATED)
    
class PropertyUpdateTextFieldsView(APIView):
    """Handles PATCH requests for updating only text fields in a Property."""

    def patch(self, request, *args, **kwargs):
        try:
            print("Incoming Request Data:", request.data)
            # Fetch the property instance based on the provided ID (from the URL)
            property_instance = Property.objects.get(id=kwargs['pk'])  # 'pk' is the property ID in URL

            # Fields that are allowed to be updated
            allowed_fields = [
                'air_code', 'folio_number', 'description', 'property_rating', 
                'room_capacity', 'people_capacity', 'deposit_amount', 'rent_amount'
            ]

            # Extract the fields to update from the request data
            update_data = {field: value for field, value in request.data.items() if field in allowed_fields}

            if not update_data:
                return Response({"detail": "No valid fields to update."}, status=status.HTTP_400_BAD_REQUEST)

            if "folio_number" in update_data:
                print(f"Updating folio_number from {property_instance.folio_number} to {update_data['folio_number']}")
                property_instance.folio_number = update_data["folio_number"]
                property_instance.save()  # Explicitly save it
                print("Manually Updated folio_number:", property_instance.folio_number)
            # Use PropertySerializer to validate the data
            serializer = PropertySerializer(property_instance, data=update_data, partial=True)
            serializer.is_valid(raise_exception=True)  # Raises ValidationError if any fields are invalid
            serializer.save()  # Save the updated property instance
            print("Updated folio_number:", property_instance.folio_number)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Property.DoesNotExist:
            return Response({"detail": "Property not found."}, status=status.HTTP_404_NOT_FOUND)

        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"Error: {e}")
            return Response({"detail": "An error occurred while updating the property."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RoomImageUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        print("🚀 Upload request received...")
        
        # Debugging request data
        print("📝 Full request data:", request.data)
        print("📂 Uploaded files:", request.FILES)

        property_id = request.data.get('property_id')  # Get property ID from frontend
        image = request.FILES.get('image')
        description = request.data.get('description', '')

        # Validate required fields
        if not property_id:
            print("❌ Missing property_id in request!")
            return Response({"error": "Property ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        if not image:
            print("❌ No image file received!")
            return Response({"error": "Image file is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve property instance
        try:
            property_instance = Property.objects.get(id=property_id)
            print(f"✅ Found Property: {property_instance}")
        except Property.DoesNotExist:
            print("❌ Property not found with ID:", property_id)
            return Response({"error": "Property not found."}, status=status.HTTP_404_NOT_FOUND)

        # Upload image to Cloudinary
        try:
            print("📡 Uploading image to Cloudinary...")
            upload_result = cloudinary.uploader.upload(image)
            print("✅ Cloudinary upload success:", upload_result)
            image_url = upload_result.get('secure_url')
            image_public_id = upload_result.get('public_id')
        except Exception as e:
            print("❌ Cloudinary upload failed:", str(e))
            return Response({"error": "Failed to upload image."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Save Room Image
        print("💾 Saving image to database...")
        room_image = RoomImage.objects.create(
            property=property_instance,
            image=image_public_id,  # Store Cloudinary public ID
            description=description
        )

        print("✅ Room image saved successfully:", room_image)

        serializer = RoomImageSerializer(room_image)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
class AllCustomUsersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = CustomUser.objects.all()
        serializer = CustomUserSerializer(users, many=True)
        return Response(serializer.data)
    
class TenancyRequestViewSet(viewsets.ModelViewSet):
    queryset = TenancyRequest.objects.all()
    serializer_class = TenancyRequestSerializer
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def list(self, request, *args, **kwargs):
        """
        List all TenancyRequest instances for the authenticated user.
        """
        user = request.user
        tenancy_requests = TenancyRequest.objects.filter(owner=user)
        serializer = self.get_serializer(tenancy_requests, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        Create a new TenancyRequest instance when a user requests a property.
        """
        if not request.user.is_authenticated:
            return Response({"error": "Authentication is required to create a tenancy request."},
                            status=status.HTTP_401_UNAUTHORIZED)

        try:
            property_id = request.data.get('property_id')
            if not property_id:
                return Response({"error": "Property ID is required."}, status=status.HTTP_400_BAD_REQUEST)

            tenant = request.user  # Get authenticated user (tenant)

            try:
                property_instance = Property.objects.get(id=property_id)
            except Property.DoesNotExist:
                return Response({"error": "Property not found."}, status=status.HTTP_404_NOT_FOUND)

            owner = property_instance.owner

            # Create the tenancy request
            tenancy_request = TenancyRequest.objects.create(
                property=property_instance,
                tenant=tenant,  # The tenant is the authenticated user
                owner=owner,    # The owner is from the property
                status='pending'
            )

            # Return the response with the created tenancy request details
            return Response(TenancyRequestSerializer(tenancy_request).data, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(f"Error creating tenancy request: {e}")
            return Response({"error": "An error occurred while sending the tenancy request."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        print(f"Attempting to fetch TenancyRequest with pk: {pk}")

        # Get the TenancyRequest instance using the primary key (pk)
        tenancy_request = self.get_object()

        print(f"TenancyRequest found: {tenancy_request.id}, Status: {tenancy_request.status}")
        
        try:
            # Call the 'approve' method on the model to handle the logic
            print("Calling the 'approve' method on TenancyRequest instance...")
            tenancy_request.approve()

            print("TenancyRequest approved successfully.")
            
            # Return a successful response
            return Response({"status": "approved"}, status=status.HTTP_200_OK)
        
        except ValueError as e:
            # If the request is not in 'pending' status
            print(f"Error: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # For any other errors (e.g., database errors)
            print(f"An error occurred during approval: {e}")
            return Response({"error": "An error occurred while processing the approval."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    # Custom action to reject a tenancy request
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        tenancy_request = self.get_object()
        if tenancy_request.status == "pending":
            tenancy_request.status = "rejected"
            tenancy_request.save()
            return Response({"status": "rejected"}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid status for rejection."}, status=status.HTTP_400_BAD_REQUEST)

class TenantTenancyRequestViewSet(viewsets.ModelViewSet):
    """
    List all TenancyRequest instances where the authenticated user is the tenant.
    """
    queryset = TenancyRequest.objects.all()
    serializer_class = TenancyRequestSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        """
        List all TenancyRequest instances for the authenticated user where they are the tenant.
        """
       
        tenancy_requests = TenancyRequest.objects.filter(tenant=request.user)
        
        # Optionally filter by status if provided
        status_param = request.query_params.get('status', None)
        if status_param:
            tenancy_requests = tenancy_requests.filter(status=status_param)

        # Serialize and return data
        serializer = self.get_serializer(tenancy_requests, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Delete a TenancyRequest instance for the authenticated user where they are the tenant.
        """
        try:
            # Get the TenancyRequest instance
            tenancy_request = self.get_object()

            # Ensure the request belongs to the authenticated user (tenant)
            if tenancy_request.tenant != request.user:
                return Response({'detail': 'You are not authorized to delete this request.'}, status=status.HTTP_403_FORBIDDEN)

            # Delete the tenancy request
            tenancy_request.delete()

            return Response({'detail': 'Request deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)

        except TenancyRequest.DoesNotExist:
            return Response({'detail': 'Request not found.'}, status=status.HTTP_404_NOT_FOUND)
        
class OwnerPaymentView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def get(self, request):
        # Get the logged-in user
        user = request.user
        # Filter properties by the owner (logged-in user)
        properties = Property.objects.filter(owner=user)
        
        # Serialize the filtered properties
        serializer = PropertySerializer(properties, many=True)
        
        # Return the serialized data in the response
        return Response(serializer.data, status=status.HTTP_200_OK)