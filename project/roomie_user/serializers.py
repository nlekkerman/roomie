from rest_framework import serializers
from django.contrib.auth.models import User
from .models import CustomUser, AddressHistory
from roomie_property.models import Property

class AddressHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AddressHistory
        fields = ['id', 'user', 'address', 'start_date', 'end_date']

class CustomUserSerializer(serializers.ModelSerializer):
    # Nested serializer for the address history
    address_history = AddressHistorySerializer(many=True, read_only=True)
    
    # Explicitly define the fields to be serialized
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    user_rating_in_app = serializers.DecimalField(max_digits=3, decimal_places=1)
    phone_number = serializers.CharField(max_length=15, allow_blank=True, required=False)
    address = serializers.PrimaryKeyRelatedField(queryset=Property.objects.all(), required=False)
    first_name = serializers.CharField(max_length=30, allow_blank=True, required=False)
    last_name = serializers.CharField(max_length=30, allow_blank=True, required=False)
    email = serializers.EmailField(required=False, allow_blank=True)
    has_address = serializers.BooleanField(default=False)

    class Meta:
        model = CustomUser
        fields = ['id', 'user', 'first_name', 'last_name','user_rating_in_app', 'phone_number', 'address', 'email', 'has_address', 'address_history']

    def create(self, validated_data):
        # Create CustomUser instance
        user_data = validated_data.pop('user')
        user_instance = User.objects.create(**user_data)
        custom_user = CustomUser.objects.create(user=user_instance, **validated_data)
        return custom_user

    def update(self, instance, validated_data):
        # Update the CustomUser instance
        instance.user.first_name = validated_data.get('first_name', instance.user.first_name)
        instance.user.last_name = validated_data.get('last_name', instance.user.last_name)
        instance.user.email = validated_data.get('email', instance.user.email)
        instance.user.save()

        instance.user_rating_in_app = validated_data.get('user_rating_in_app', instance.user_rating_in_app)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.address = validated_data.get('address', instance.address)
        instance.has_address = validated_data.get('has_address', instance.has_address)
        
        instance.save()
        return instance
