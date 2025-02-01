from rest_framework import viewsets
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import RentPayment, PropertyPayments, UserCashFlow, PropertyCashFlow
from .serializers import (
    RentPaymentSerializer, 
    PropertyPaymentsSerializer, 
    UserCashFlowSerializer, 
    PropertyCashFlowSerializer,
    UserSerializer
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

class RentPaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Rent Payments with optional filters for status and property"""

    queryset = RentPayment.objects.all()
    serializer_class = RentPaymentSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Get the status and property filters from the request query parameters
        status_filter = self.request.query_params.get('status', None)
        property_filter = self.request.query_params.get('property', None)

        # Filter by status if provided
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Filter by property if provided
        if property_filter:
            queryset = queryset.filter(property__id=property_filter)  # Filtering based on property ID

        return queryset


class PropertyPaymentsViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Property Payments with embedded Property Billings"""
    queryset = PropertyPayments.objects.all().prefetch_related('property_billings')
    serializer_class = PropertyPaymentsSerializer

class UserCashFlowViewSet(viewsets.ModelViewSet):
    serializer_class = UserCashFlowSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_fields = ['category', 'status']  # Allow filtering by category and status
    ordering_fields = ['date']  # You can also allow ordering by date, for example

    def get_queryset(self):
        """
        This method will return only the cash flows for the currently authenticated user.
        It also applies any filtering for category and status.
        """
        user = self.request.user  # Get the current authenticated user
        return UserCashFlow.objects.filter(user=user)  # Filter cash flows by the user

    @action(detail=True, methods=['patch'], url_path='mark_to_pay_order')
    def mark_to_pay_order(self, request, pk=None):
        try:
            cash_flow = self.get_object()  # Gets the object with the given pk (id)
            cash_flow.to_pay_order = not cash_flow.to_pay_order  # Toggle the value
            cash_flow.save()
            return Response({'message': 'Cash flow updated successfully.'}, status=status.HTTP_200_OK)
        except UserCashFlow.DoesNotExist:
            return Response({'error': 'Cash flow not found'}, status=status.HTTP_404_NOT_FOUND)
class PropertyCashFlowViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Property Cash Flow"""
    queryset = PropertyCashFlow.objects.all()
    serializer_class = PropertyCashFlowSerializer

class UsersInPaymentsViewSet(viewsets.ViewSet):
    """ViewSet to retrieve all users involved in Rent or Property Payments"""

    def list(self, request):
        # Get all unique users involved in Rent and Property Payments
        rent_users = User.objects.filter(tenant_bills__isnull=False).distinct()
        property_users = User.objects.filter(property_billing__isnull=False).distinct()

        # Combine querysets and ensure uniqueness
        all_users = rent_users.union(property_users)

        serializer = UserSerializer(all_users, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """Retrieve a specific user and their associated payments, with optional filters for status or category"""
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        # Get query parameters for filtering by status or category
        status_filter = request.query_params.get('status', None)
        category_filter = request.query_params.get('category', None)

        # Fetch Rent Payments for this user with optional status filter
        rent_payments = RentPayment.objects.filter(tenant_billings__tenant=user)
        if status_filter:
            rent_payments = rent_payments.filter(status=status_filter)

        # Fetch Property Payments for this user with optional filters
        property_payments = PropertyPayments.objects.filter(property_billings__tenant=user)
        if status_filter:
            property_payments = property_payments.filter(status=status_filter)
        if category_filter:
            property_payments = property_payments.filter(category=category_filter)

        # Combine data
        payment_data = {
            "user": UserSerializer(user).data,
            "rent_payments": rent_payments.values('id', 'date', 'amount', 'status'),
            "property_payments": property_payments.values('id', 'date', 'category', 'amount', 'status')
        }

        return Response(payment_data)