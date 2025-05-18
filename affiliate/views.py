from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from .serializers import BecomeAffiliateSerializer, AffiliateWalletSerializer
from authentication.permissions import IsAdminOrReadOnly, IsOwner
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import transaction
from .models import AffiliateWallet




class BecomeAffiliateView(GenericAPIView):
    
    serializer_class = BecomeAffiliateSerializer
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="Become an Affiliate",
        operation_description="Create an affiliate account for the authenticated user.",
        request_body=BecomeAffiliateSerializer,
        responses={
            201: openapi.Response("Affiliate Created", BecomeAffiliateSerializer),
            400: "Bad Request",
            403: "Forbidden"
        }
    )
    
    @transaction.atomic
    def post(self, request):
        """
        Create an affiliate account for the authenticated user.
        """
        
        serializer = self.get_serializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Affiliate account created successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "success": False,
            "message": "Failed to create affiliate account.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)



class AffiliateWalletView(GenericAPIView):
    """
    View to get the affiliate wallet details.
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = AffiliateWalletSerializer
    queryset = AffiliateWallet.objects.all()
    
    @swagger_auto_schema(
        operation_summary="Get Affiliate Wallet",
        operation_description="Retrieve the wallet details of the authenticated affiliate.",
        responses={
            200: openapi.Response("Affiliate Wallet Details", AffiliateWalletSerializer),
            403: "Forbidden"
        }
    )
    
    def get(self, request):
        """
        Retrieve the wallet details of the authenticated affiliate.
        """
        
        try:
            user = request.user
            if not hasattr(user, 'affiliate'):
                return Response({
                    "success": False,
                    "message": "You are not an affiliate."
                }, status=status.HTTP_403_FORBIDDEN)
            wallet = user.affiliate.wallet
            serializer = self.get_serializer(wallet)
            return Response({
                "success": True,
                "Message": "Affiliate wallet details retrieved successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except AffiliateWallet.DoesNotExist:
            return Response({
                "success": False,
                "message": "Affiliate wallet does not exist."
            }, status=status.HTTP_404_NOT_FOUND)