from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from accounts.models import Seller, Shop, Buyer, BuyerShippingAddress, BuyerPaymentMethod
from accounts.serializers import (
    SellerSerializer, 
    ShopSerializer, 
    BuyerSerializer, 
    BuyerShippingAddressSerializer, 
    BuyerPaymentMethodSerializer, 
    RegionSerializer, 
    ProvinceSerializer, 
    CitySerializer, 
    BarangaySerializer, 
    CountrySerializer
)

import logging

logger = logging.getLogger(__name__)


@extend_schema_view(
    list=extend_schema(
        summary="List all Sellers",
        description="Returns a paginated list of all Sellers in the system with optional filtering.",
        parameters=[
            OpenApiParameter(
                name="user_type",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter sellers by user type (e.g., 'seller')",
                required=False
            ),
            OpenApiParameter(
                name="is_verified",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="Filter by verification status",
                required=False
            ),
            OpenApiParameter(
                name="is_active",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="Filter by active status",
                required=False
            ),
            OpenApiParameter(
                name="is_premium_plan",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="Filter by premium plan status",
                required=False
            ),
        ],
        examples=[
            OpenApiExample(
                'Success Response',
                value={
                    "count": 1,
                    "next": None,
                    "previous": None,
                    "results": [
                        {
                            "seller_id": "uuid-string",
                            "user": {
                                "user_id": "uuid-string",
                                "mobile_no": "09088648123",
                                "first_name": "John",
                                "last_name": "Doe",
                                "email": "john@example.com",
                                "user_type": "seller"
                            },
                            "shop": {
                                "shop_id": "uuid-string",
                                "shop_name": "John's Water Shop",
                                "shop_type": "water",
                                "is_active": True,
                                "is_verified": False
                            },
                            "is_verified": False,
                            "is_active": True,
                            "is_premium_plan": False
                        }
                    ]
                }
            )
        ],
        tags=["Seller Management"]
    ),
    create=extend_schema(
        summary="Create a new Seller",
        description="Create a new Seller account with associated user and shop information.",
        request=SellerSerializer,
        responses={
            201: SellerSerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                'Create Seller Request',
                value={
                    "user": {
                        "mobile_no": "09088648123",
                        "first_name": "John",
                        "last_name": "Doe",
                        "email": "john@example.com",
                        "user_type": "seller",
                        "address1": "123 Main St",
                        "city": 1,
                        "province": 1,
                        "region": 1,
                        "country": 1,
                        "password": "securepass123"
                    },
                    "shop": {
                        "shop_type": "water",
                        "shop_name": "John's Water Shop",
                        "shop_short_name": "JWS",
                        "shop_address1": "123 Main St",
                        "shop_contact_number": "09088648123",
                        "shop_contact_person": "John Doe",
                        "shop_email": "john@shop.com"
                    },
                    "is_verified": False,
                    "is_active": True
                }
            )
        ],
        tags=["Seller Management"]
    ),
    retrieve=extend_schema(
        summary="Get Seller details",
        description="Retrieve detailed information for a specific Seller.",
        responses={
            200: SellerSerializer,
            404: OpenApiTypes.OBJECT,
        },
        tags=["Seller Management"]
    ),
    update=extend_schema(
        summary="Update Seller information",
        description="Update Seller account and associated information.",
        request=SellerSerializer,
        responses={
            200: SellerSerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        tags=["Seller Management"]
    ),
    partial_update=extend_schema(
        summary="Partially update Seller information",
        description="Partially update Seller account and associated information.",
        request=SellerSerializer,
        responses={
            200: SellerSerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        tags=["Seller Management"]
    ),
    destroy=extend_schema(
        summary="Delete Seller account",
        description="Delete a Seller account and associated data.",
        responses={
            204: None,
            404: OpenApiTypes.OBJECT,
        },
        tags=["Seller Management"]
    ),
)
class SellerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Seller accounts.
    
    Provides CRUD operations for Seller entities including:
    - List all sellers with filtering options
    - Create new seller accounts with shops
    - Retrieve seller details
    - Update seller information
    - Delete seller accounts
    """
    queryset = Seller.objects.select_related('user').all()
    serializer_class = SellerSerializer
    lookup_field = 'seller_id'
    
    def get_queryset(self):
        """
        Custom queryset with optional filtering.
        """
        queryset = Seller.objects.select_related('user').all()
        
        # Filter by user type
        user_type = self.request.query_params.get('user_type', None)
        if user_type:
            queryset = queryset.filter(user__user_type=user_type)
        
        # Filter by verification status
        is_verified = self.request.query_params.get('is_verified', None)
        if is_verified is not None:
            is_verified_bool = is_verified.lower() == 'true'
            queryset = queryset.filter(is_verified=is_verified_bool)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            is_active_bool = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active_bool)
        
        # Filter by premium plan status
        is_premium = self.request.query_params.get('is_premium_plan', None)
        if is_premium is not None:
            is_premium_bool = is_premium.lower() == 'true'
            queryset = queryset.filter(is_premium_plan=is_premium_bool)
        
        logger.info(f"Seller queryset filtered: {queryset.count()} results")
        return queryset
    
    def perform_create(self, serializer):
        """
        Custom create logic with logging.
        """
        seller = serializer.save()
        logger.info(f"New seller created: {seller.seller_id} - {seller.user.get_full_name()}")
        return seller
    
    def perform_update(self, serializer):
        """
        Custom update logic with logging.
        """
        seller = serializer.save()
        logger.info(f"Seller updated: {seller.seller_id} - {seller.user.get_full_name()}")
        return seller
    
    def perform_destroy(self, instance):
        """
        Custom delete logic with logging.
        """
        seller_name = instance.user.get_full_name()
        seller_id = instance.seller_id
        instance.delete()
        logger.info(f"Seller deleted: {seller_id} - {seller_name}")
    
    @extend_schema(
        summary="Get seller profile",
        description="Retrieve detailed profile information for the authenticated seller.",
        responses={
            200: SellerSerializer,
            401: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        tags=["Seller Management"]
    )
    @action(detail=False, methods=['get'], url_path='profile')
    def profile(self, request):
        """
        Get the profile of the currently authenticated seller.
        """
        try:
            seller = Seller.objects.get(user=request.user)
            serializer = self.get_serializer(seller)
            logger.info(f"Profile retrieved for seller: {seller.user.get_full_name()}")
            return Response(serializer.data)
        except Seller.DoesNotExist:
            logger.warning(f"Profile not found for user: {request.user.mobile_no}")
            return Response(
                {"error": "Seller profile not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @extend_schema(
        summary="Get seller statistics",
        description="Retrieve statistics and analytics for sellers.",
        responses={
            200: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
        },
        tags=["Seller Management"]
    )
    @action(detail=False, methods=['get'], url_path='statistics')
    def statistics(self, request):
        """
        Get statistics for the authenticated seller.
        """
        try:
            seller = Seller.objects.get(user=request.user)
            
            # Get shop statistics (Shop has ForeignKey to Seller)
            try:
                shop = Shop.objects.get(seller=seller)
                shop_stats = {
                    "shop_name": shop.shop_name,
                    "shop_type": shop.shop_type,
                    "is_active": shop.is_active,
                    "is_verified": shop.is_verified,
                    "is_featured": shop.is_featured,
                    "total_products": 0,  # Placeholder for future product count
                    "total_orders": 0,    # Placeholder for future order count
                    "total_revenue": 0,   # Placeholder for future revenue calculation
                }
            except Shop.DoesNotExist:
                shop_stats = None
            
            # Get seller statistics
            seller_stats = {
                "seller_id": str(seller.seller_id),
                "is_verified": seller.is_verified,
                "is_active": seller.is_active,
                "is_premium_plan": seller.is_premium_plan,
                "is_free_plan": seller.is_free_plan,
                "premium_expiry": seller.is_premium_plan_expiry,
                "shop": shop_stats
            }
            
            logger.info(f"Statistics retrieved for seller: {seller.user.get_full_name()}")
            return Response(seller_stats)
            
        except Seller.DoesNotExist:
            logger.warning(f"Statistics not found for user: {request.user.mobile_no}")
            return Response(
                {"error": "Seller profile not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @extend_schema(
        summary="Update seller verification status",
        description="Update the verification status of a seller account.",
        request=OpenApiTypes.OBJECT,
        responses={
            200: SellerSerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                'Update Verification Request',
                value={
                    "is_verified": True,
                    "is_active": True
                }
            )
        ],
        tags=["Seller Management"]
    )
    @action(detail=True, methods=['patch'], url_path='update-status')
    def update_status(self, request, seller_id=None):
        """
        Update seller verification and active status.
        """
        try:
            seller = self.get_object()
            is_verified = request.data.get('is_verified')
            is_active = request.data.get('is_active')
            
            if is_verified is not None:
                seller.is_verified = is_verified
            
            if is_active is not None:
                seller.is_active = is_active
            
            seller.save()
            serializer = self.get_serializer(seller)
            
            logger.info(f"Status updated for seller: {seller.seller_id} - {seller.user.get_full_name()}")
            return Response(serializer.data)
            
        except Seller.DoesNotExist:
            return Response(
                {"error": "Seller not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @extend_schema(
        summary="Get seller shops",
        description="Retrieve all shops associated with a seller.",
        responses={
            200: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        tags=["Seller Management"]
    )
    @action(detail=True, methods=['get'], url_path='shops')
    def shops(self, request, seller_id=None):
        """
        Get all shops for a specific seller.
        """
        try:
            seller = self.get_object()
            shops = Shop.objects.filter(seller=seller)
            shop_serializer = ShopSerializer(shops, many=True)
            
            logger.info(f"Shops retrieved for seller: {seller.user.get_full_name()}")
            return Response({
                "seller": seller.user.get_full_name(),
                "shops": shop_serializer.data
            })
            
        except Seller.DoesNotExist:
            return Response(
                {"error": "Seller not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @extend_schema(
        summary="Activate premium plan",
        description="Activate premium plan for a seller account.",
        request=OpenApiTypes.OBJECT,
        responses={
            200: SellerSerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                'Activate Premium Request',
                value={
                    "is_premium_plan": True,
                    "is_premium_plan_expiry": "2025-12-31"
                }
            )
        ],
        tags=["Seller Management"]
    )
    @action(detail=True, methods=['patch'], url_path='activate-premium')
    def activate_premium(self, request, seller_id=None):
        """
        Activate premium plan for a seller.
        """
        try:
            seller = self.get_object()
            is_premium = request.data.get('is_premium_plan', False)
            expiry_date = request.data.get('is_premium_plan_expiry')
            
            if is_premium:
                seller.is_premium_plan = True
                seller.is_free_plan = False
                if expiry_date:
                    seller.is_premium_plan_expiry = expiry_date
            else:
                seller.is_premium_plan = False
                seller.is_free_plan = True
                seller.is_premium_plan_expiry = None
            
            seller.save()
            serializer = self.get_serializer(seller)
            
            logger.info(f"Premium plan updated for seller: {seller.seller_id} - {seller.user.get_full_name()}")
            return Response(serializer.data)
            
        except Seller.DoesNotExist:
            return Response(
                {"error": "Seller not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @extend_schema(
        summary="Get seller dashboard data",
        description="Retrieve comprehensive dashboard data for the authenticated seller.",
        responses={
            200: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        tags=["Seller Management"]
    )
    @action(detail=False, methods=['get'], url_path='dashboard')
    def dashboard(self, request):
        """
        Get dashboard data for the authenticated seller.
        """
        try:
            seller = Seller.objects.get(user=request.user)
            
            # Get shop data (Shop has ForeignKey to Seller)
            try:
                shop = Shop.objects.get(seller=seller)
                shop_info = {
                    "shop_id": str(shop.shop_id),
                    "shop_name": shop.shop_name,
                    "shop_type": shop.shop_type,
                    "shop_status": "Active" if shop.is_active else "Inactive",
                    "is_verified": shop.is_verified,
                    "is_featured": shop.is_featured
                }
            except Shop.DoesNotExist:
                shop_info = None
            
            dashboard_data = {
                "seller_info": {
                    "seller_id": str(seller.seller_id),
                    "name": seller.user.get_full_name(),
                    "mobile_no": seller.user.mobile_no,
                    "email": seller.user.email,
                    "is_verified": seller.is_verified,
                    "is_active": seller.is_active,
                    "plan_type": "Premium" if seller.is_premium_plan else "Free",
                    "premium_expiry": seller.is_premium_plan_expiry
                },
                "shop_info": shop_info,
                "quick_stats": {
                    "total_products": 0,      # Placeholder
                    "total_orders": 0,        # Placeholder
                    "pending_orders": 0,      # Placeholder
                    "total_revenue": 0,       # Placeholder
                    "monthly_revenue": 0      # Placeholder
                },
                "recent_activity": []         # Placeholder for recent orders/activities
            }
            
            logger.info(f"Dashboard data retrieved for seller: {seller.user.get_full_name()}")
            return Response(dashboard_data)
            
        except Seller.DoesNotExist:
            logger.warning(f"Dashboard data not found for user: {request.user.mobile_no}")
            return Response(
                {"error": "Seller profile not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
