from rest_framework import serializers
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'confirm_password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')  # Remove confirm_password before creating user
        user = User.objects.create_user(**validated_data)
        return user
