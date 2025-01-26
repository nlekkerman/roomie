from rest_framework import viewsets
from .models import UserCashFlow
from .serializers import UserCashFlowSerializer
from rest_framework.response import Response

class UserCashFlowViewSet(viewsets.ModelViewSet):
    queryset = UserCashFlow.objects.all()
    serializer_class = UserCashFlowSerializer

    def get_queryset(self):
        queryset = self.queryset

        # Filter by user if user ID is provided in the URL
        user_id = self.request.query_params.get('user', None)
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        # Filter by category if category is provided
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)

        # Filter by status if status is provided
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
