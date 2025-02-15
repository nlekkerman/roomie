from rest_framework import serializers
from .models import Property, PropertyTenantRecords, RoomImage, TenancyRequest
from django.contrib.auth.models import User



class RoomImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    def get_image_url(self, obj):
        """Construct the full Cloudinary image URL using the stored public ID."""
        if obj.image:  # Ensure image is not None
            return f"https://res.cloudinary.com/dg0ssec7u/image/upload/{obj.image}"
        return None  # Return None if no image exists

    class Meta:
        model = RoomImage
        fields = ['id', 'property', 'image', 'image_url', 'description']  # Include property_id

    def create(self, validated_data):
        """Ensure property_id is correctly assigned when creating a RoomImage."""
        property_id = self.context.get("property_id")  # Expect property_id in serializer context
        
        if not property_id:
            raise serializers.ValidationError({"property_id": "This field is required."})
        
        try:
            property_instance = Property.objects.get(id=property_id)
        except Property.DoesNotExist:
            raise serializers.ValidationError({"property_id": "Property not found."})

        validated_data['property'] = property_instance  # Assign the correct property
        return super().create(validated_data)

class PropertyTenantRecordsSerializer(serializers.ModelSerializer):
    property = serializers.PrimaryKeyRelatedField(queryset=Property.objects.all())  # Assuming Property is related here
    tenant = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())  # Assuming User model is being used for tenant
    start_date = serializers.DateField()
    end_date = serializers.DateField(allow_null=True)

    class Meta:
        model = PropertyTenantRecords
        fields = [ 'property', 'tenant', 'start_date', 'end_date']

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
        

class TenancyRequestSerializer(serializers.ModelSerializer):
    tenant_username = serializers.ReadOnlyField(source="tenant.username")
    owner_username = serializers.ReadOnlyField(source="owner.username")
    property_address = serializers.ReadOnlyField(source="property.full_address")
    tenant_first_name = serializers.SerializerMethodField()
    tenant_last_name = serializers.SerializerMethodField()
    tenant_email = serializers.SerializerMethodField()
    tenant_phone = serializers.SerializerMethodField()

    class Meta:
        model = TenancyRequest
        fields = ["id", "tenant","tenant_first_name", "tenant_last_name", "tenant_email", "tenant_phone", 'tenant_rating', "tenant_username", "property", "property_address", "owner", "owner_username", "request_date", "status"]

    def update(self, instance, validated_data):
        # Check if the action is 'approve' and call the approve method on the model
        if validated_data.get('status') == 'approved':
            instance.approve()  # Call the model's approve method
        
        # You can also add any additional validation or changes before saving
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance

    def get_tenant_rating(self, obj):
        return obj.tenant.user_rating_in_app
    
    def get_tenant_first_name(self, obj):
        return obj.tenant_first_name()

    def get_tenant_last_name(self, obj):
        return obj.tenant_last_name()

    def get_tenant_email(self, obj):
        return obj.tenant_email()

    def get_tenant_phone(self, obj):
        return obj.tenant_phone()
