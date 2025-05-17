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



class AddUserBankAccountView(GenericAPIView):
    """
    View to add a bank account for a user
    """
    
    serializer_class = UserBankAccountSerializer
    permission_classes = [IsAuthenticated]
    
    
    @swagger_auto_schema(
        operation_summary="Add User Bank Account",
        operation_description="Add a bank account for the authenticated user.",
        request_body=UserBankAccountSerializer,
        responses={
            201: openapi.Response("User Bank Account Created", UserBankAccountSerializer),
            400: "Bad Request",
            401: "Unauthorized",
        }
    )
    
    @transaction.atomic
    def post(self, request):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Bank account added successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        print("SERIALIZER ERRORS:", serializer.errors)
        return Response({
            "success": False,
            "message": "Failed to add bank account.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)