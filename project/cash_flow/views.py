from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import UserCashFlow, PropertyCashFlow, RentPayment, TenantBilling
from .serializers import UserCashFlowSerializer, PropertyCashFlowSerializer, RentPaymentSerializer, TenantBillingSerializer
from django.contrib.auth.models import User
from roomie_property.models import Property

class UserCashFlowViewSet(viewsets.ModelViewSet):
    queryset = UserCashFlow.objects.all()
    serializer_class = UserCashFlowSerializer

    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>\d+)/cash_flow')
    def get_user_cash_flow(self, request, user_id=None):
        # Filter by user ID and status (optional)
        status = request.query_params.get('status', None)
        if status:
            user_cash_flows = UserCashFlow.objects.filter(user__id=user_id, status=status)
        else:
            user_cash_flows = UserCashFlow.objects.filter(user__id=user_id)
        serializer = self.get_serializer(user_cash_flows, many=True)
        return Response(serializer.data)


class PropertyCashFlowViewSet(viewsets.ModelViewSet):
    queryset = PropertyCashFlow.objects.all()
    serializer_class = PropertyCashFlowSerializer

    @action(detail=False, methods=['get'], url_path='property/(?P<property_id>\d+)/cash_flow')
    def get_property_cash_flow(self, request, property_id=None):
        # Filter by property ID and status (paid or pending)
        status = request.query_params.get('status', None)
        if status:
            property_cash_flows = PropertyCashFlow.objects.filter(property__id=property_id, status=status)
        else:
            property_cash_flows = PropertyCashFlow.objects.filter(property__id=property_id)
        serializer = self.get_serializer(property_cash_flows, many=True)
        return Response(serializer.data)


class RentPaymentViewSet(viewsets.ModelViewSet):
    queryset = RentPayment.objects.all()
    serializer_class = RentPaymentSerializer

    @action(detail=False, methods=['get'], url_path='property/(?P<property_id>\d+)/rent_payments')
    def get_property_rent_payments(self, request, property_id=None):
        # Filter by property ID and status (paid or pending)
        status = request.query_params.get('status', None)
        if status:
            rent_payments = RentPayment.objects.filter(property__id=property_id, status=status)
        else:
            rent_payments = RentPayment.objects.filter(property__id=property_id)
        serializer = self.get_serializer(rent_payments, many=True)
        return Response(serializer.data)


class TenantBillingViewSet(viewsets.ModelViewSet):
    queryset = TenantBilling.objects.all()
    serializer_class = TenantBillingSerializer

    @action(detail=False, methods=['get'], url_path='rent_payment/(?P<rent_payment_id>\d+)/tenant_billings')
    def get_tenant_billings_for_rent_payment(self, request, rent_payment_id=None):
        # Filter by rent payment ID
        tenant_billings = TenantBilling.objects.filter(rent_payment__id=rent_payment_id)
        serializer = self.get_serializer(tenant_billings, many=True)
        return Response(serializer.data)
