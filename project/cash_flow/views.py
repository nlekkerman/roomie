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


import logging
logger = logging.getLogger(__name__)

class PropertyPaymentsViewSet(viewsets.ModelViewSet):
    queryset = PropertyPayments.objects.all().prefetch_related('property_billings')
    serializer_class = PropertyPaymentsSerializer

    def list(self, request, *args, **kwargs):
        logger.info("Received request for Property Payments list")
        payments = self.get_queryset()
        logger.info(f"Database query result: {payments}")  # Log the queryset result

        if not payments:
            logger.info("No payments found")
            return Response({"message": "No property payments available."}, status=200)

        serializer = self.get_serializer(payments, many=True)
        logger.info(f"Serialized data: {serializer.data}")
        return Response(serializer.data)

class UserCashFlowViewSet(viewsets.ModelViewSet):
    """ViewSet for managing User Cash Flows with optional filters for category, status, and order to pay"""

    serializer_class = UserCashFlowSerializer
    permission_classes = [IsAuthenticated]
    
    # Use filtering and ordering
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_fields = ['category', 'status']  # Filter by category and status
    ordering_fields = ['date']  # Allow ordering by date
    
    def get_queryset(self):
        """
        Return only the cash flows for the authenticated user, with optional filtering and ordering.
        """
        user = self.request.user  # Get the authenticated user
        queryset = UserCashFlow.objects.filter(user=user)

        # Apply filters (category and status)
        category_filter = self.request.query_params.get('category', None)
        if category_filter:
            queryset = queryset.filter(category=category_filter)

        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset

    @action(detail=True, methods=['patch'], url_path='mark_to_pay_order')
    def mark_to_pay_order(self, request, pk=None):
        """
        Toggle the 'to_pay_order' field for the specific cash flow (identified by pk).
        """
        try:
            cash_flow = self.get_object()  # Fetch the object by its primary key (pk)
            cash_flow.to_pay_order = not cash_flow.to_pay_order  # Toggle the order flag
            cash_flow.save()  # Save the updated cash flow
            return Response({'message': 'Cash flow updated successfully.'}, status=status.HTTP_200_OK)
        except UserCashFlow.DoesNotExist:
            return Response({'error': 'Cash flow not found.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], url_path='filter-by-category')
    def filter_by_category(self, request):
        """
        Filter cash flows by category.
        """
        category = request.query_params.get('category', None)
        if not category:
            return Response({"detail": "Category filter is required."}, status=400)

        cash_flows = self.get_queryset().filter(category=category)
        serializer = self.get_serializer(cash_flows, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='filter-by-status')
    def filter_by_status(self, request):
        """
        Filter cash flows by status.
        """
        status = request.query_params.get('status', None)
        if not status:
            return Response({"detail": "Status filter is required."}, status=400)

        cash_flows = self.get_queryset().filter(status=status)
        serializer = self.get_serializer(cash_flows, many=True)
        return Response(serializer.data)
    
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