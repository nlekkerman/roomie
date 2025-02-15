# serializers.py

from rest_framework import serializers
from .models import UserCashFlow, PropertyCashFlow, PropertyPayments, PropertyBilling, TenantBilling,RentPayment
from roomie_property.models import Property
from django.contrib.auth.models import User
from datetime import datetime
# User serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class RentPaymentSerializer(serializers.ModelSerializer):
    tenant_billings = serializers.SerializerMethodField()

    class Meta:
        model = RentPayment
        fields = '__all__'

    def get_tenant_billings(self, obj):
        """Fetches and serializes related TenantBilling objects for this RentPayment"""
        return [
            {
                "tenant": billing.tenant.username,
                "amount": billing.amount,
                "status": billing.status,
                "deadline": billing.deadline,
                "category": billing.category
            }
            for billing in obj.tenant_billings.all()
        ]
# UserCashFlow serializer
class UserCashFlowSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    property_billing = serializers.PrimaryKeyRelatedField(queryset=PropertyBilling.objects.all(), required=False)
    tenant_billing = serializers.PrimaryKeyRelatedField(queryset=TenantBilling.objects.all(), required=False)

    class Meta:
        model = UserCashFlow
        fields = ['id', 'user', 'amount', 'date', 'description', 'category', 'status', 'deadline', 'to_pay_order', 'property_billing', 'tenant_billing']

# PropertyCashFlow serializer
class PropertyCashFlowSerializer(serializers.ModelSerializer):
    property = serializers.PrimaryKeyRelatedField(queryset=Property.objects.all())

    class Meta:
        model = PropertyCashFlow
        fields = ['id', 'property', 'amount', 'date', 'description', 'category', 'status', 'deadline']


class PropertyPaymentsSerializer(serializers.ModelSerializer):
    property_billings = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()  # Override the date field

    class Meta:
        model = PropertyPayments
        fields = '__all__'

    def get_date(self, obj):
        """Ensure date is returned as a date (not datetime)."""
        if isinstance(obj.date, datetime):
            return obj.date.date()  # Convert datetime to date
        return obj.date

    def get_property_billings(self, obj):
        return [
            {
                "tenant": billing.tenant.username,
                "amount": billing.amount,
                "status": billing.status,
                "deadline": billing.deadline,
                "category": billing.category
            }
            for billing in obj.property_billings.all()
        ]
    property_billings = serializers.SerializerMethodField()

    class Meta:
        model = PropertyPayments
        fields = '__all__'

    def get_property_billings(self, obj):
        # Serialize the related PropertyBilling objects
        billings_data = [
            {
                "tenant": billing.tenant.username,
                "amount": billing.amount,
                "status": billing.status,
                "deadline": billing.deadline,
                "category": billing.category
            }
            for billing in obj.property_billings.all()
        ]
        print(f"Property Billings for payment {obj.id}: ", billings_data)  # Print the serialized billing data
        return billings_data