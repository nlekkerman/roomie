import logging
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.utils.timezone import now
from rest_framework.parsers import JSONParser
from .models import DamageRepairReport, RepairImage, Notification
from roomie_user.models import CustomUser
from .serializers import DamageRepairReportSerializer, RepairImageSerializer, NotificationSerializer

# Set up logging
logger = logging.getLogger(__name__)
class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(receiver=self.request.user, is_read=False).order_by('-created_at')

    @action(detail=False, methods=['POST'])
    def mark_as_read(self, request):
        Notification.objects.filter(receiver=request.user, is_read=False).update(is_read=True)
        return Response({'message': 'Notifications marked as read'}, status=status.HTTP_200_OK)


class DamageRepairReportViewSet(viewsets.ModelViewSet):
    queryset = DamageRepairReport.objects.all()
    serializer_class = DamageRepairReportSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'tenant', 'property']
    search_fields = ['description', 'property__street', 'tenant__username']
    ordering_fields = ['reported_at', 'status']
    parser_classes = (MultiPartParser, FormParser, JSONParser)  # Support file uploads
   
    @action(detail=True, methods=['patch'], url_path="update-status")
    def update_status(self, request, pk=None):
        """Allow owners to update the repair status."""
        try:
            print(f"🔧 Updating status for repair ID {pk}")
            repair = self.get_object()
            new_status = request.data.get("status")

            print(f"➡️ New status received: {new_status}")

            if new_status not in dict(DamageRepairReport.REPORT_STATUS_CHOICES):
                print(f"❌ Invalid status value: {new_status}")
                return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

            repair.status = new_status

            if new_status == "resolved":
                repair.resolved_at = now()

            repair.save()

            return Response({"message": "Status updated successfully", "new_status": repair.status})
        
        except DamageRepairReport.DoesNotExist:
            print("❌ Repair request not found")
            return Response({"error": "Repair request not found"}, status=status.HTTP_404_NOT_FOUND)
    
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return response

    def create(self, request, *args, **kwargs):
        """Override create method to automatically assign tenant and property."""
        # Handle multiple image uploads
        images = request.FILES.getlist('repair_images')  # Multiple file upload support

        # Serialize incoming data and check if it's valid
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            # Save the report instance (but do not save to DB yet)
            report = serializer.save()

            # Fetch the authenticated user (tenant)
            user = request.user
            print(f"Authenticated User: {user.username}")  # Debug: Print the authenticated user

            # Ensure the user has a valid CustomUser profile
            try:
                custom_user = CustomUser.objects.get(user=user)
                print(f"CustomUser found for {user.username}: {custom_user}")  # Debug: Print CustomUser data
            except CustomUser.DoesNotExist:
                print(f"❌ CustomUser profile not found for user {user.username}")
                return Response({"error": "CustomUser profile not found for the authenticated user."}, 
                                status=status.HTTP_404_NOT_FOUND)

            # Automatically assign the tenant (CustomUser) to the damage report
            report.tenant = custom_user.user  # Link the CustomUser (tenant) to the damage report
            print(f"Assigned tenant: {custom_user.user.username}")  # Debug: Tenant association

            # Check if a property is associated with the tenant (CustomUser)
            if not custom_user.address:
                print(f"❌ No property associated with tenant {user.username}")
                return Response({"error": "Property not found for this user."}, status=status.HTTP_400_BAD_REQUEST)

            # If no property is provided in the request, we auto-assign the CustomUser's property
            if 'property' not in request.data:  # If no property is provided in the request
                report.property = custom_user.address  # Assign the property from CustomUser
                print(f"Property assigned to the report: {custom_user.address.full_address()}")  # Debug: Property assignment
            
            # Save the report instance
            report.save()

            # Handle uploaded images if any
            for img in images:
                RepairImage.objects.create(damage_report=report, image=img)

            # Serialize the response with necessary information
            report_data = serializer.data
            tenant = report.tenant
            property_address = report.property.full_address() if report.property else "No Address"

            # Add tenant username and property address to the response
            report_data['tenant_username'] = tenant.username if tenant else "No Tenant"
            report_data['property_address'] = property_address

            # Log the creation and return the response
            logger.info("Damage report created successfully: %s", report_data)
            return Response(report_data, status=status.HTTP_201_CREATED)
        
        # If the serializer is invalid, return errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RepairImageViewSet(viewsets.ModelViewSet):
    queryset = RepairImage.objects.all()
    serializer_class = RepairImageSerializer
    permission_classes = [IsAuthenticated]  # Ensure authenticated access
    filterset_fields = ['damage_report']
    search_fields = ['description']

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return response
