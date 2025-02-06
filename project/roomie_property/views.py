# views.py

from rest_framework import viewsets, status
from rest_framework.views import APIView
from .models import Property, RoomImage
from .serializers import PropertySerializer, OwnerPropertiesSerializer, RoomImageSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action


class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    parser_classes = [MultiPartParser, FormParser]

    def partial_update(self, request, *args, **kwargs):
        """Handles PATCH requests for updating images"""

        try:
            property_instance = self.get_object()
            
            # Handle main image update
            if 'main_image' in request.FILES:
                property_instance.main_image = request.FILES['main_image']
                property_instance.save()
                print(f"Main image updated: {property_instance.main_image.url}")

            # Handle room images update
            if 'room_image' in request.FILES:
                room_images = request.FILES.getlist('room_image')
                print(f"Inside partial_update method. Room images count: {len(room_images)}")

                # Get existing image filenames (Cloudinary public IDs or extracted filenames)
                existing_images = [
                    img.image.public_id.split("/")[-1] for img in property_instance.room_images.all()
                ]
                print(f"Existing images filenames: {existing_images}")

                for img in room_images:
                    print(f"Adding room image: {img.name}")

                    # Extract the public ID from the image URL (assumed to be passed from frontend)
                    img_public_id = img.name.split("/").pop().split(".")[0]  # Extract Cloudinary public ID
                    print(f"Deleting old image: {img_public_id}")
                    
                    # Check if the image exists in the database and delete it
                    if 'existing_image_public_id' in request.data:
                        existing_public_id = request.data['existing_image_public_id']
                        # Delete the image using the existing public ID
                        property_instance.room_images.filter(image__contains=existing_public_id).delete()
                        print(f"Deleted old image with public ID: {existing_public_id}")

                    # Save new image
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
            raise ValidationError("An error occurred while updating the property.")

    @action(detail=True, methods=['patch'])
    def update_text_fields(self, request, *args, **kwargs):
        """Handles PATCH requests for updating text fields."""
        try:
            property_instance = self.get_object()
            data = request.data.copy()  # Copy the request data for modification

            # Ensure only text fields are updated
            text_fields = ['air_code', 'folio_number', 'description', 'property_rating', 
                           'room_capacity', 'people_capacity', 'deposit_amount', 'rent_amount']
            text_data = {field: data[field] for field in text_fields if field in data}

            # Use the PropertySerializer to validate and update the instance
            serializer = self.get_serializer(property_instance, data=text_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error: {e}")
            return Response({"detail": "An error occurred while updating the property."}, status=status.HTTP_400_BAD_REQUEST)
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

class PropertyCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser]  # To handle file uploads (image files)

    def post(self, request, *args, **kwargs):
        # Handling the creation of the property with the main image and room images
        property_data = request.data.copy()  # Copy request data to ensure we don't modify the original

        # Retrieve the files (images)
        main_image = request.FILES.get('main_image')
        room_images = request.FILES.getlist('room_images')

        # Create the Property instance with owner automatically set to the logged-in user
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

        # Handling room images if any
        for img in room_images:
            RoomImage.objects.create(
                property=property,
                image=img,
                description='Room image description'  # You can add logic to dynamically set description
            )

        # Return the property data with the owner info
        return Response(PropertySerializer(property).data, status=status.HTTP_201_CREATED)
    
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .models import Property
from .serializers import PropertySerializer

class PropertyUpdateTextFieldsView(APIView):
    """Handles PATCH requests for updating only text fields in a Property."""

    def patch(self, request, *args, **kwargs):
        try:
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

            # Use PropertySerializer to validate the data
            serializer = PropertySerializer(property_instance, data=update_data, partial=True)
            serializer.is_valid(raise_exception=True)  # Raises ValidationError if any fields are invalid
            serializer.save()  # Save the updated property instance

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Property.DoesNotExist:
            return Response({"detail": "Property not found."}, status=status.HTTP_404_NOT_FOUND)

        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"Error: {e}")
            return Response({"detail": "An error occurred while updating the property."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)