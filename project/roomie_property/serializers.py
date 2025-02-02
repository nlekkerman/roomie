from rest_framework import serializers
from .models import Property, PropertyTenantRecords, RoomImage
from django.contrib.auth.models import User

# ✅ Serializer for Room Images
class RoomImageSerializer(serializers.ModelSerializer):
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

    # ✅ Add main image and related room images
    main_image = serializers.ImageField(use_url=True)
    room_images = RoomImageSerializer(many=True, read_only=True)

    class Meta:
        model = Property
        fields = ['id', 'street', 'house_number', 'town', 'county', 'country', 'property_rating', 
                  'room_capacity', 'people_capacity', 'owner', 'owner_username', 'deposit_amount', 
                  'rent_amount', 'property_supervisor', 'property_supervisor_name', 
                  'main_image', 'room_images',  # ✅ Include images
                  'current_tenant', 'tenant_history', 'all_current_tenant']
