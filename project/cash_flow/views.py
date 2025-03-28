from rest_framework import viewsets
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import RentPayment, PropertyPayments, UserCashFlow, PropertyCashFlow
from datetime import datetime
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
from django.shortcuts import get_object_or_404
from roomie_property.models import Property
import logging
logger = logging.getLogger(__name__)

class RentPaymentViewSet(viewsets.ModelViewSet):
    queryset = RentPayment.objects.all()
    serializer_class = RentPaymentSerializer

    def create(self, request, *args, **kwargs):
        """Ensure 'deadline' field is only a date (strip time part if needed)"""
        mutable_data = request.data.copy()  # ✅ Make request data mutable

        deadline = mutable_data.get('deadline')
        if deadline:
            try:
                # Convert string datetime to just date (handling different formats)
                if "T" in deadline:
                    deadline = datetime.fromisoformat(deadline).date()  # ✅ Handles ISO format safely
                else:
                    deadline = datetime.strptime(deadline, "%Y-%m-%d").date()

                mutable_data["deadline"] = deadline
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=mutable_data)  # ✅ Use modified data
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PropertyPaymentsViewSet(viewsets.ModelViewSet):
    """Viewset for handling property payments, ensuring only owners manage their payments."""
    serializer_class = PropertyPaymentsSerializer
    permission_classes = [IsAuthenticated]  # Ensure user is logged in

    def get_queryset(self):
        """Restrict the queryset to only payments for properties owned by the authenticated user."""
        user = self.request.user
        if user.is_authenticated:
            return PropertyPayments.objects.filter(property__owner=user).prefetch_related('property_billings')
        return PropertyPayments.objects.none()

    def list(self, request, *args, **kwargs):
        """Return a list of property payments related to the authenticated user."""
        logger.info("Received request for Property Payments list")
        
        payments = self.get_queryset()
        if not payments.exists():
            logger.info("No payments found for this user.")
            return Response({"message": "No property payments available."}, status=status.HTTP_200_OK)

        serializer = self.get_serializer(payments, many=True)
        logger.info(f"Serialized payments data: {serializer.data}")
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """Allow owners to create payments only for their properties."""
        user = request.user
        if not user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        property_id = request.data.get("property")  # Get the selected property ID

        if not property_id:
            return Response({"error": "Property selection is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure the property belongs to the logged-in owner
        property_obj = get_object_or_404(Property, id=property_id, owner=user)

        # Validate and save the payment
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(property=property_obj)  # Assign the validated property
            logger.info(f"Payment created: {serializer.data}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        logger.error(f"Payment creation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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