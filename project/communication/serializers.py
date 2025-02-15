from rest_framework import serializers
from .models import DamageRepairReport, RepairImage,Notification
from roomie_property.models import Property
from cloudinary.utils import cloudinary_url
from roomie_user.models import CustomUser
from rest_framework.exceptions import NotFound
from django.contrib.auth.models import User
from accounts_app.serializers import UserSerializer

class NotificationSerializer(serializers.ModelSerializer):
    sender = UserSerializer()
    receiver = UserSerializer()
    
    class Meta:
        model = Notification
        fields = ['id', 'sender', 'receiver', 'message', 'created_at', 'is_read']
class RepairImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = RepairImage
        fields = ['id', 'image', 'description']

    def get_image(self, obj):
        if obj.image:
            return cloudinary_url(obj.image.public_id)[0]  # ✅ Automatically generate full URL
        return None


class DamageRepairReportSerializer(serializers.ModelSerializer):
    repair_images = RepairImageSerializer(many=True, read_only=True)
    tenant = serializers.SerializerMethodField()  # Tenant's username
    property_address = serializers.SerializerMethodField()  # Property address

    class Meta:
        model = DamageRepairReport
        fields = [
            'id', 'property', 'tenant', 'description', 'status', 'reported_at',
            'resolved_at', 'repair_images', 'property_address'
        ]

    def get_tenant(self, obj):
        """Return the username of the tenant."""
        return obj.tenant.username if obj.tenant else None

    def get_property_address(self, obj):
        """Return the full address of the property associated with the tenant."""
        if obj.tenant:
            custom_user = CustomUser.objects.filter(user=obj.tenant).first()  # Get the associated CustomUser
            if custom_user and custom_user.address:
                return custom_user.address.full_address()  # Assuming your Property model has a full_address() method
        return None

    def create(self, validated_data):
        """Override create method to automatically assign tenant and property."""
        
        user = self.context['request'].user  # Get the authenticated user (tenant)
        print(f"Authenticated User: {user.username}")  # Debug print for user
        
        # Automatically assign the tenant to the report
        validated_data['tenant'] = user
        print(f"Tenant assigned: {user.username}")  # Debug print for tenant
        
        # Fetch the CustomUser profile (tenant's data)
        try:
            custom_user = CustomUser.objects.get(user=user)  # Retrieve the CustomUser based on the authenticated user
            print(f"CustomUser found: {custom_user.user.username}")  # Debug print for CustomUser
        except CustomUser.DoesNotExist:
            raise NotFound("CustomUser profile not found for the authenticated user.")
        
        # Ensure that the CustomUser has a valid address (property)
        if custom_user.address is None:
            print(f"CustomUser {user.username} does not have a property assigned.")  # Debug print
            raise NotFound(f"Property not found for user {user.username}.")
        else:
            print(f"CustomUser {user.username} has address: {custom_user.address.full_address()}")  # Debug print for property

        # If no property is provided, assign the tenant's property based on the CustomUser model
        if 'property' not in validated_data:
            validated_data['property'] = custom_user.address  # Automatically assign property
            print(f"Property assigned: {custom_user.address.full_address()}")  # Debug print for property assignment

        # Create the damage repair report instance
        print("Creating Damage Repair Report...")  # Debug print before report creation
        return super().create(validated_data)
