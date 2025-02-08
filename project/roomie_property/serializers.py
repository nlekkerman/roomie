from rest_framework import serializers
from .models import Property, PropertyTenantRecords, RoomImage
from django.contrib.auth.models import User



class RoomImageSerializer(serializers.ModelSerializer):
    # Prepend the base URL for room images
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        # Assuming your cloud storage URL is defined in your settings or is consistent
    
        return obj.image.url

    class Meta:
        model = RoomImage
        fields = ['id', 'image', 'description']
class PropertyTenantRecordsSerializer(serializers.ModelSerializer):
    tenant = serializers.StringRelatedField()  # Display tenant username
    
    class Meta:
        model = PropertyTenantRecords
        fields = ['id', 'tenant', 'start_date', 'end_date']

class PropertySerializer(serializers.ModelSerializer):
    current_tenant = PropertyTenantRecordsSerializer(many=False, read_only=True)
    all_current_tenant = PropertyTenantRecordsSerializer(many=True, read_only=True)
    tenant_history = PropertyTenantRecordsSerializer(many=True, read_only=True) 

    property_supervisor_name = serializers.CharField(source='property_supervisor.username', read_only=True)
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    folio_number = serializers.CharField(required=False, allow_blank=True, max_length=50)  # This makes folio_number writable and allows blanks
    main_image = serializers.ImageField(required=False, allow_null=True)    
    room_images = RoomImageSerializer(required=False, many=True)
    air_code = serializers.CharField(max_length=10, allow_blank=True, required=False)
    description = serializers.CharField(allow_blank=True, required=False)
    class Meta:
        model = Property
        fields = ['id', 'street', 'house_number', 'town', 'county', 'country', 'property_rating', 
                  'room_capacity', 'people_capacity', 'owner', 'owner_username', 'deposit_amount', 
                  'rent_amount', 'property_supervisor', 'property_supervisor_name',
                  'main_image', 'room_images',
                  'current_tenant', 'tenant_history', 'all_current_tenant', 'folio_number',
                  'air_code', 'description']
    
    
    def update(self, instance, validated_data):
        
        # Handle text fields update (air_code, description, etc.)
        text_fields = ['air_code', 'folio_number', 'description', 'property_rating', 
                       'room_capacity', 'people_capacity', 'deposit_amount', 'rent_amount']
        
        for field in text_fields:
            if field in validated_data:
                setattr(instance, field, validated_data[field])
                print(f"Updated {field}: {validated_data[field]}")
        # Handle Main Image Update
        if 'main_image' in validated_data:
            instance.main_image = validated_data['main_image']
            print(f"Main image updated: {instance.main_image.url}")

        # Handle Room Images Update
        if 'room_images' in validated_data:
            room_images_data = validated_data.pop('room_images')
            instance.room_images.all().delete()  # Remove old images

            for image_data in room_images_data:
                RoomImage.objects.create(property=instance, **image_data)  # Add new images

        instance.save()
        return instance

class OwnerPropertiesSerializer(serializers.ModelSerializer):
    # This serializer returns properties owned by the user
    class Meta:
        model = Property
        fields = ['id', 'street', 'house_number', 'town', 'county', 'country', 'property_rating', 'rent_amount', 'deposit_amount', 'main_image']
    owned_properties = PropertySerializer(many=True, read_only=True)

    class Meta:
        model = User  # The owner is a User
        fields = ['id', 'username', 'owned_properties']