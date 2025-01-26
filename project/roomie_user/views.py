# views.py
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser
from .serializers import CustomUserSerializer

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    # Optionally, you can override the retrieve and update methods for custom behavior
    def retrieve(self, request, pk=None):
        try:
            custom_user = CustomUser.objects.get(pk=pk)
            serializer = self.get_serializer(custom_user)
            return Response(serializer.data)
        except CustomUser.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None):
        try:
            custom_user = CustomUser.objects.get(pk=pk)
            serializer = self.get_serializer(custom_user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
