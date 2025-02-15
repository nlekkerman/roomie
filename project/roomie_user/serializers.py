from rest_framework import serializers
from django.contrib.auth.models import User
from .models import CustomUser, AddressHistory
from roomie_property.models import Property

class AddressHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AddressHistory
        fields = ['id', 'user', 'address', 'start_date', 'end_date']

class CustomUserSerializer(serializers.ModelSerializer):
    address_history = AddressHistorySerializer(many=True, read_only=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    user_rating_in_app = serializers.DecimalField(max_digits=3, decimal_places=1)
    phone_number = serializers.CharField(max_length=15, allow_blank=True, required=False)
    address = serializers.PrimaryKeyRelatedField(queryset=Property.objects.all(), required=False)
    first_name = serializers.CharField(max_length=30, allow_blank=True, required=False)
    last_name = serializers.CharField(max_length=30, allow_blank=True, required=False)
    email = serializers.EmailField(required=False, allow_blank=True)
    has_address = serializers.BooleanField(default=False)
    profile_image = serializers.ImageField(required=False, allow_null=True)  # Allowing null images
    property_id = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = [
            'user', 'first_name', 'last_name', 'user_rating_in_app', 
            'phone_number', 'address', 'email', 'has_address', 
            'address_history', 'profile_image', 'property_id'
        ]

    def create(self, validated_data):
        user_instance = validated_data.pop('user', None)

        if not user_instance:
            user_instance = self.context.get('request').user

        if not user_instance:
            raise serializers.ValidationError("User is required")

        if CustomUser.objects.filter(user=user_instance).exists():
            raise serializers.ValidationError("Custom user profile already exists.")

        # Default values if not provided
        validated_data.setdefault('first_name', user_instance.first_name)
        validated_data.setdefault('last_name', user_instance.last_name)
        validated_data.setdefault('email', user_instance.email)
        validated_data.setdefault('user_rating_in_app', 5.0)

        profile_image = validated_data.pop('profile_image', None)

        # Create the CustomUser instance
        custom_user = CustomUser(**validated_data)
        custom_user.user = user_instance  
        custom_user.pk = user_instance.pk

        try:
            custom_user.save(force_insert=True)
        except Exception as e:
            raise serializers.ValidationError(f"Database error: {str(e)}")

        if profile_image:
            custom_user.profile_image = profile_image
            custom_user.save()

        return custom_user

    
    
    def update(self, instance, validated_data):
        """
        Update an existing CustomUser with profile image.
        """
        instance.user.first_name = validated_data.get('first_name', instance.user.first_name)
        instance.user.last_name = validated_data.get('last_name', instance.user.last_name)
        instance.user.email = validated_data.get('email', instance.user.email)
        instance.user.save()

        instance.user_rating_in_app = validated_data.get('user_rating_in_app', instance.user_rating_in_app)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.address = validated_data.get('address', instance.address)
        instance.has_address = validated_data.get('has_address', instance.has_address)

        profile_image = validated_data.get('profile_image', None)
        if profile_image is not None: 
            instance.profile_image = profile_image
        
        instance.save()
        return instance
    
    def get_current_address(self, obj):
        # Fetch the current active address from AddressHistory
        print(f"Fetching current address for user: {obj.user.username}")
        current_address = AddressHistory.objects.filter(user=obj, end_date__isnull=True).first()
        print(f"Found current address: {current_address}")  # This will print None if no address is found
        if current_address:
            print(f"Current address: {current_address.address}")
        return current_address.address if current_address else None

    def get_property_id(self, obj):
        # Look for the current active address from the AddressHistory table
        current_address = AddressHistory.objects.filter(user=obj, end_date__isnull=True).first()
        
        if current_address and current_address.address:
            # Assuming AddressHistory has a ForeignKey to Property
            property = current_address.address.property  # This assumes your Address model has a 'property' field
            return property.id if property else None
        return None