from rest_framework import serializers
from .models import DamageRepairReport, RepairImage
from roomie_property.models import Property
from cloudinary.utils import cloudinary_url
from roomie_user.models import CustomUser
from rest_framework.exceptions import NotFound

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

        # Automatically assign the tenant to the report
        validated_data['tenant'] = user

        # Fetch the CustomUser profile (tenant's data)
        try:
            custom_user = CustomUser.objects.get(user=user)  # Retrieve the CustomUser based on the authenticated user
        except CustomUser.DoesNotExist:
            raise NotFound("CustomUser profile not found for the authenticated user.")

        # If no property is provided, assign the tenant's property based on the CustomUser model
        if 'property' not in validated_data:
            # Assuming the CustomUser has a related property, like `address` field pointing to a Property
            if custom_user.address:
                validated_data['property'] = custom_user.address
            else:
                raise NotFound("Property not found for this user.")

        # Create the damage repair report instance
        return super().create(validated_data)
