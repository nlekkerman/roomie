# serializers.py

from rest_framework import serializers
from .models import Property, PropertyTenantRecords
from django.contrib.auth.models import User

class PropertyTenantRecordsSerializer(serializers.ModelSerializer):
    tenant = serializers.StringRelatedField()  # Use StringRelatedField to display tenant username
    class Meta:
        model = PropertyTenantRecords
        fields = ['id', 'tenant', 'start_date', 'end_date']

class PropertySerializer(serializers.ModelSerializer):
    current_tenant = PropertyTenantRecordsSerializer(many=False, read_only=True)
    tenant_history = PropertyTenantRecordsSerializer(many=True, read_only=True)  # Include tenant history

    class Meta:
        model = Property
        fields = ['id', 'street', 'house_number', 'town', 'county', 'country', 'property_rating', 
                  'room_capacity', 'people_capacity', 'owner', 'property_supervisor', 'current_tenant', 
                  'tenant_history']
