import logging
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated

from .models import DamageRepairReport, RepairImage
from .serializers import DamageRepairReportSerializer, RepairImageSerializer

# Set up logging
logger = logging.getLogger(__name__)

class DamageRepairReportViewSet(viewsets.ModelViewSet):
    queryset = DamageRepairReport.objects.all()
    serializer_class = DamageRepairReportSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'tenant', 'property']
    search_fields = ['description', 'property__street', 'tenant__username']
    ordering_fields = ['reported_at', 'status']
    parser_classes = (MultiPartParser, FormParser)  # 🔥 Support file uploads

    def list(self, request, *args, **kwargs):
        logger.info("Fetching damage reports with filters: %s", request.query_params)
        response = super().list(request, *args, **kwargs)
        logger.info("Fetched reports: %s", response.data)
        return response

    def create(self, request, *args, **kwargs):
        logger.info("Received new damage report: %s", request.data)

        # Handle multiple image uploads
        images = request.FILES.getlist('repair_images')
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            report = serializer.save()

            # Save uploaded images
            for img in images:
                RepairImage.objects.create(damage_report=report, image=img)

            # Serialize the response with the necessary property address and tenant name
            report_data = serializer.data
            tenant = report.tenant
            property_address = report.property.full_address() if report.property else "No Address"

            # Append tenant and property address information to the response
            report_data['tenant_username'] = tenant.username if tenant else "No Tenant"
            report_data['property_address'] = property_address

            logger.info("Damage report created successfully: %s", report_data)
            return Response(report_data, status=status.HTTP_201_CREATED)
        
        logger.error("Error creating damage report: %s", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RepairImageViewSet(viewsets.ModelViewSet):
    queryset = RepairImage.objects.all()
    serializer_class = RepairImageSerializer
    permission_classes = [IsAuthenticated]  # 🔒 Ensure authenticated access
    filterset_fields = ['damage_report']
    search_fields = ['description']

    def list(self, request, *args, **kwargs):
        logger.info("Fetching repair images with filters: %s", request.query_params)
        response = super().list(request, *args, **kwargs)
        logger.info("Fetched images: %s", response.data)
        return response
