from django.shortcuts import render
from .serializers import CampaignSerializer, CategorySerializer
from rest_framework.generics import GenericAPIView
from .models import Campaign, Category
from authentication.permissions import IsAdminOrReadOnly, IsOwner
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import transaction




class CategoryListView(GenericAPIView):
    """"
    View to list all categories.
    """
    
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    
    def get_permissions(self):
        """
        Assign permissions based on the request method.
        """
        if self.request.method in ['POST']:
            return [IsAdminOrReadOnly()]
        return [IsAuthenticated()]
    
    @swagger_auto_schema(
        operation_summary="List Categories",
        operation_description="Retrieve a list of all categories.",
        responses={
            200: openapi.Response("Categories List", CategorySerializer(many=True)),
        }
    )
    def get(self, request):
        categories = self.get_queryset()
        serializer = self.get_serializer(categories, many=True)
        return Response({
            "success": True,
            "message": "Categories retrieved successfully." if categories else "No categories available.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_summary="Create Category (Admin Only)",
        request_body=CategorySerializer,
        responses={
            201: openapi.Response("Category Created", CategorySerializer),
            400: "Bad Request",
            403: "Forbidden"
        }
    )
    @transaction.atomic
    def post(self, request):
        serialiazer = self.get_serializer(data=request.data)
        if serialiazer.is_valid():
            category = serialiazer.save()
            return Response({
                "success": True,
                "message": "Category created successfully.",
                "data": CategorySerializer(category).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "success": False,
            "message": "Validation failed",
            "errors": serialiazer.errors
        }, status=status.HTTP_400_BAD_REQUEST)



class CampaignListView(GenericAPIView):
    """"
    View to list all campaigns.
    """
    
    serializer_class = CampaignSerializer
    queryset = Campaign.objects.all()
    
    def get_permissions(self,):
        if self.request.method in ['POST']:
            return [IsAuthenticated()]
        else:
            return [AllowAny()]
    
    @swagger_auto_schema(
        operation_summary="List Campaigns",
        operation_description="Retrieve a list of all campaigns.",
        responses={
            200: openapi.Response("Campaigns List", CampaignSerializer(many=True)),
        }
    )
    def get(self, request):
        campaigns = self.get_queryset()
        serializer = self.get_serializer(campaigns, many=True)
        return Response({
            "success": True,
            "message": "Campaigns retrieved successfully." if campaigns else "No campaigns available.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_summary="Create Campaign",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['title', 'description', 'goal', 'image', 'category_id'],
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING),
                'description': openapi.Schema(type=openapi.TYPE_STRING),
                'goal': openapi.Schema(type=openapi.TYPE_NUMBER),
                'image': openapi.Schema(type=openapi.TYPE_FILE),
                'category_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'start_date': openapi.Schema(type=openapi.TYPE_STRING, format='date'),
                'end_date': openapi.Schema(type=openapi.TYPE_STRING, format='date'),
            }
        ),
        responses={
            201: openapi.Response("Campaign Created", CampaignSerializer),
            400: "Bad Request",
            401: openapi.Response("Unauthorized", openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    "message": openapi.Schema(type=openapi.TYPE_STRING),
                }
            )),
        }
    )
    
    @transaction.atomic
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            campaign = serializer.save()
            return Response({
                "success": True,
                "message": "Campaign created successfully.",
                "data": CampaignSerializer(campaign).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "success": False,
            "message": "Validation failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)



class CampaignDetailView(GenericAPIView):
    """
    View to retrieve, update, or delete a specific campaign.
    """
    serializer_class = CampaignSerializer
    
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'DELETE']:
            return [IsAuthenticated(), IsOwner(), IsAdminOrReadOnly()]
        else:
            return [AllowAny()]
    
    
    def get_object(self, slug):
        try:
            campaign = Campaign.objects.get(slug=slug)
            self.check_object_permissions(self.request, campaign)
            return campaign
        except Campaign.DoesNotExist:
            return None
    
    
    @swagger_auto_schema(
        operation_summary="Retrieve Campaign",
        operation_description="Retrieve a specific campaign by slug.",
        responses={
            200: openapi.Response("Campaign Details", CampaignSerializer),
            404: "Campaign Not Found"
        }
    )
    
    def get(self, request, slug):
        campaign = self.get_object(slug)
        if not campaign:
            return Response({
                "success": False,
                "message": "Campaign not found."
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(campaign)
        return Response({
            "success": True,
            "message": "Campaign retrieved successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_summary="Update Campaign",
        operation_description="Update a specific campaign by slug.",
        request_body=CampaignSerializer,
        responses={
            200: openapi.Response("Campaign Updated", CampaignSerializer),
            400: "Validation Error",
            404: "Campaign Not Found"
        }
    )
    @transaction.atomic
    def put(self, request, slug):
        campaign = self.get_object(slug)
        if not campaign:
            return Response({
                "success": False,
                "message": "Campaign not found."
            }, status=status.HTTP_404_NOT_FOUND)
        
        if campaign != request.user:
            return Response({
                "success": False,
                "message": "You do not have permission to edit this campaign."
            }, status=status.HTTP_403_FORBIDDEN)
        
        serialiazer = self.get_serializer(campaign, data=request.data, partial=True)
        if serialiazer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Campaign updated successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            "success": False,
            "message": "Validation failed.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_summary="Delete Campaign",
        operation_description="Delete a specific campaign by slug.",
        responses={
            204: "Campaign Deleted",
            404: "Campaign Not Found"
        }
    )
    
    @transaction.atomic
    def delete(self, request, slug):
        campaign = self.get_object(slug)
        if not campaign:
            return Response({
                "success": False,
                "message": "Campaign not found."
            }, status=status.HTTP_404_NOT_FOUND)
        
        if campaign != request.user:
            return Response({
                "success": False,
                "message": "You do not have permission to delete this campaign."
            }, status=status.HTTP_403_FORBIDDEN)
        
        campaign.delete()
        return Response({
            "success": True,
            "message": "Campaign deleted successfully."
        }, status=status.HTTP_204_NO_CONTENT)
