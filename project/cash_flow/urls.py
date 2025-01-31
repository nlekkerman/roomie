from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RentPaymentViewSet, PropertyPaymentsViewSet, UserCashFlowViewSet, PropertyCashFlowViewSet,UsersInPaymentsViewSet

router = DefaultRouter()
router.register(r'rent-payments', RentPaymentViewSet, basename='rentpayment')
router.register(r'property-payments', PropertyPaymentsViewSet, basename='propertypayment')
router.register(r'user-cashflow', UserCashFlowViewSet, basename='usercashflow')
router.register(r'property-cashflow', PropertyCashFlowViewSet, basename='propertycashflow')
router.register(r'users-in-payments', UsersInPaymentsViewSet, basename='usersinpayments')

urlpatterns = [
    path('', include(router.urls)),
]
