from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserCashFlowViewSet, PropertyCashFlowViewSet, RentPaymentViewSet, TenantBillingViewSet

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'user_cash_flows', UserCashFlowViewSet)
router.register(r'property_cash_flows', PropertyCashFlowViewSet)
router.register(r'rent_payments', RentPaymentViewSet)
router.register(r'tenant_billings', TenantBillingViewSet)

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]
