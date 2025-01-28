from rest_framework import serializers
from .models import UserCashFlow, PropertyCashFlow, RentPayment, TenantBilling
from django.contrib.auth.models import User
from roomie_property.models import Property

# First, define TenantBillingSerializer
class TenantBillingSerializer(serializers.ModelSerializer):
    rent_payment = serializers.PrimaryKeyRelatedField(queryset=RentPayment.objects.all())
    tenant = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = TenantBilling
        fields = ['id', 'rent_payment', 'tenant', 'amount', 'status', 'deadline']


# Now, define RentPaymentSerializer which uses TenantBillingSerializer
class RentPaymentSerializer(serializers.ModelSerializer):
    property = serializers.PrimaryKeyRelatedField(queryset=Property.objects.all())
    tenant_billings = TenantBillingSerializer(many=True, read_only=True)

    class Meta:
        model = RentPayment
        fields = ['id', 'property', 'amount', 'date', 'description', 'status', 'deadline', 'tenant_billings']


# Then, define PropertyCashFlowSerializer
class PropertyCashFlowSerializer(serializers.ModelSerializer):
    property = serializers.PrimaryKeyRelatedField(queryset=Property.objects.all())  # Adjust this based on your Property model

    class Meta:
        model = PropertyCashFlow
        fields = ['id', 'property', 'amount', 'date', 'description', 'category', 'status', 'deadline']


# Finally, define UserCashFlowSerializer
class UserCashFlowSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = UserCashFlow
        fields = ['id', 'user','first_name', 'last_name', 'amount', 'date', 'description', 'category', 'status', 'deadline', 'to_pay_order']
