from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from .models import PaystackBank, UserBankAccount
from .serializers import PaystackBankSerializer, UserBankAccountSerializer
from authentication.permissions import IsAdminOrReadOnly, IsOwner
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import transaction






class PaystackBankListView(GenericAPIView):
    """
    View to list all paystack banks.
    """
    
    
    queryset = PaystackBank.objects.all()
    permission_classes = [AllowAny]
    pagination_class = None
    serializer_class = PaystackBankSerializer
    
    
    @swagger_auto_schema(
        operation_summary="List Paystack Banks",
        operation_description="Retrieve a list of all paystack banks.",
        responses={
            200: openapi.Response("Paystack Banks List", PaystackBankSerializer(many=True)),
        }
    )
    
    def get(self, request):
        """
        Retrieve a list of all paystack banks.
        """
        
        banks = self.get_queryset()
        serializer = self.get_serializer(banks, many=True)
        return Response({
            "success": True,
            "message": "Paystack banks retrieved successfully." if banks else "No paystack banks available.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)