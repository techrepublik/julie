from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from accounts.models import Buyer, BuyerShippingAddress, BuyerPaymentMethod
from accounts.serializers import (
    BuyerSerializer, 
    BuyerShippingAddressSerializer, 
    BuyerPaymentMethodSerializer
)

import logging

logger = logging.getLogger(__name__)


@extend_schema_view(
    list=extend_schema(
        summary="List all Buyers",
        description="Returns a paginated list of all Buyers in the system with optional filtering.",
        parameters=[
            OpenApiParameter(
                name="user_type",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter buyers by user type (e.g., 'buyer')",
                required=False
            ),
            OpenApiParameter(
                name="is_premium_customer",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="Filter by premium customer status",
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
                            "buyer_id": "uuid-string",
                            "user": {
                                "user_id": "uuid-string",
                                "mobile_no": "09088648123",
                                "first_name": "John",
                                "last_name": "Doe",
                                "email": "john@example.com",
                                "user_type": "buyer"
                            },
                            "is_premium_customer": False,
                            "preferred_payment_method": "gcash"
                        }
                    ]
                }
            )
        ],
        tags=["Buyer Management"]
    ),
    create=extend_schema(
        summary="Create a new Buyer",
        description="Create a new Buyer account with associated user information.",
        request=BuyerSerializer,
        responses={
            201: BuyerSerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                'Create Buyer Request',
                value={
                    "user": {
                        "mobile_no": "09088648123",
                        "first_name": "John",
                        "last_name": "Doe",
                        "email": "john@example.com",
                        "user_type": "buyer",
                        "address1": "123 Main St",
                        "city": "Manila",
                        "province": "Metro Manila",
                        "region": "NCR",
                        "country": "Philippines"
                    },
                    "is_premium_customer": False,
                    "preferred_payment_method": "gcash"
                }
            )
        ],
        tags=["Buyer Management"]
    ),
    retrieve=extend_schema(
        summary="Retrieve a Buyer",
        description="Get detailed information about a specific Buyer by ID.",
        responses={
            200: BuyerSerializer,
            404: OpenApiTypes.OBJECT,
        },
        tags=["Buyer Management"]
    ),
    update=extend_schema(
        summary="Update a Buyer",
        description="Update all fields of an existing Buyer account.",
        request=BuyerSerializer,
        responses={
            200: BuyerSerializer,
            400: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        tags=["Buyer Management"]
    ),
    partial_update=extend_schema(
        summary="Partially update a Buyer",
        description="Update specific fields of an existing Buyer account.",
        request=BuyerSerializer,
        responses={
            200: BuyerSerializer,
            400: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        tags=["Buyer Management"]
    ),
    destroy=extend_schema(
        summary="Delete a Buyer",
        description="Permanently delete a Buyer account and associated user data.",
        responses={
            204: None,
            404: OpenApiTypes.OBJECT,
        },
        tags=["Buyer Management"]
    ),
)
class BuyerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Buyer accounts.
    
    Provides CRUD operations for Buyer entities including:
    - List all buyers with filtering options
    - Create new buyer accounts
    - Retrieve buyer details
    - Update buyer information
    - Delete buyer accounts
    """
    queryset = Buyer.objects.select_related('user').all()
    serializer_class = BuyerSerializer
    lookup_field = 'buyer_id'
    
    def get_queryset(self):
        """
        Custom queryset with optional filtering.
        """
        queryset = Buyer.objects.select_related('user').all()
        
        # Filter by user type
        user_type = self.request.query_params.get('user_type', None)
        if user_type:
            queryset = queryset.filter(user__user_type=user_type)
        
        # Filter by premium customer status
        is_premium = self.request.query_params.get('is_premium_customer', None)
        if is_premium is not None:
            is_premium_bool = is_premium.lower() == 'true'
            queryset = queryset.filter(is_premium_customer=is_premium_bool)
        
        user_info = self.request.user.get_full_name() or self.request.user.mobile_no
        logger.info(f"Buyer queryset filtered: {queryset.count()} results by user: {user_info}")
        return queryset
    
    def perform_create(self, serializer):
        """
        Custom create logic with logging.
        """
        buyer = serializer.save()
        logger.info(f"New buyer created: {buyer.buyer_id} - {buyer.user.get_full_name()}")
        return buyer
    
    def perform_update(self, serializer):
        """
        Custom update logic with logging.
        """
        buyer = serializer.save()
        logger.info(f"Buyer updated: {buyer.buyer_id} - {buyer.user.get_full_name()}")
        return buyer
    
    def perform_destroy(self, instance):
        """
        Custom delete logic with logging.
        """
        buyer_name = instance.user.get_full_name()
        buyer_id = instance.buyer_id
        instance.delete()
        logger.info(f"Buyer deleted: {buyer_id} - {buyer_name}")
    
    @extend_schema(
        summary="Get buyer profile",
        description="Retrieve detailed profile information for the authenticated buyer.",
        responses={
            200: BuyerSerializer,
            401: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        tags=["Buyer Management"]
    )
    @action(detail=False, methods=['get'], url_path='profile')
    def profile(self, request):
        """
        Get the profile of the currently authenticated buyer.
        """
        try:
            buyer = Buyer.objects.get(user=request.user)
            serializer = self.get_serializer(buyer)
            logger.info(f"Profile retrieved for buyer: {buyer.user.get_full_name()}")
            return Response(serializer.data)
        except Buyer.DoesNotExist:
            logger.warning(f"Profile not found for user: {request.user.mobile_no}")
            return Response(
                {"error": "Buyer profile not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @extend_schema(
        summary="Get buyer statistics",
        description="Retrieve statistics and analytics for buyers.",
        responses={
            200: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
        },
        tags=["Buyer Management"]
    )
    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        """
        Get buyer statistics and analytics.
        """
        total_buyers = Buyer.objects.count()
        premium_buyers = Buyer.objects.filter(is_premium_customer=True).count()
        active_buyers = Buyer.objects.filter(user__is_active=True).count()
        
        stats = {
            "total_buyers": total_buyers,
            "premium_buyers": premium_buyers,
            "active_buyers": active_buyers,
            "premium_percentage": round((premium_buyers / total_buyers * 100), 2) if total_buyers > 0 else 0
        }
        
        logger.info(f"Buyer stats retrieved: {stats}")
        return Response(stats)
    
    @extend_schema(
        summary="Update buyer payment method",
        description="Update the preferred payment method for the authenticated buyer.",
        request=OpenApiTypes.OBJECT,
        responses={
            200: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        tags=["Buyer Management"]
    )
    @action(detail=False, methods=['put'], url_path='payment-method')
    def update_payment_method(self, request):
        """
        Update the preferred payment method for the authenticated buyer.
        """
        try:
            buyer = Buyer.objects.get(user=request.user)
            buyer.preferred_payment_method = request.data.get('preferred_payment_method', buyer.preferred_payment_method)
            buyer.save()
            logger.info(f"Buyer payment method updated: {buyer.user.get_full_name()}")
            return Response(BuyerSerializer(buyer).data)
        except Buyer.DoesNotExist:
            logger.warning(f"Buyer not found for user: {request.user.mobile_no}")
            return Response(
                {"error": "Buyer not found"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @extend_schema(
        summary="Get buyer shipping address",
        description="Retrieve the shipping address for the authenticated buyer.",
        responses={
            200: BuyerShippingAddressSerializer,
            401: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        tags=["Buyer Management"]
    )
    @action(detail=False, methods=['get'], url_path='shipping-address')
    def get_shipping_address(self, request):
        """
        Get the shipping address for the authenticated buyer.
        """
        try:
            buyer = Buyer.objects.get(user=request.user)
            shipping_addresses = BuyerShippingAddress.objects.filter(buyer=buyer)
            if shipping_addresses.exists():
                serializer = BuyerShippingAddressSerializer(shipping_addresses.first())
                logger.info(f"Shipping address retrieved for buyer: {buyer.user.get_full_name()}")
                return Response(serializer.data)
            else:
                logger.warning(f"No shipping address found for buyer: {buyer.user.get_full_name()}")
                return Response(
                    {"error": "No shipping address found"},
                    status=status.HTTP_404_NOT_FOUND
                )
        except Buyer.DoesNotExist:
            logger.warning(f"Buyer not found for user: {request.user.mobile_no}")
            return Response(
                {"error": "Buyer not found"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @extend_schema(
        summary="Update buyer shipping address",
        description="Update the shipping address for the authenticated buyer.",
        request=BuyerShippingAddressSerializer,
        responses={
            200: BuyerShippingAddressSerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        tags=["Buyer Management"]
    )
    @action(detail=False, methods=['put'], url_path='shipping-address')
    def update_shipping_address(self, request):
        """
        Update the shipping address for the authenticated buyer.
        """
        try:
            buyer = Buyer.objects.get(user=request.user)
            shipping_address, created = BuyerShippingAddress.objects.get_or_create(
                buyer=buyer,
                defaults=request.data
            )
            
            if not created:
                serializer = BuyerShippingAddressSerializer(shipping_address, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    logger.info(f"Buyer shipping address updated: {buyer.user.get_full_name()}")
                    return Response(serializer.data)
                else:
                    logger.warning(f"Invalid shipping address data for buyer: {buyer.user.get_full_name()}")
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                logger.info(f"New shipping address created for buyer: {buyer.user.get_full_name()}")
                return Response(BuyerShippingAddressSerializer(shipping_address).data)
                
        except Buyer.DoesNotExist:
            logger.warning(f"Buyer not found for user: {request.user.mobile_no}")
            return Response(
                {"error": "Buyer not found"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @extend_schema(
        summary="Get buyer settings",
        description="Retrieve the settings for the authenticated buyer.",
        responses={
            200: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
        },
        tags=["Buyer Management"]
    )
    @action(detail=False, methods=['get'], url_path='settings')
    def get_settings(self, request):
        """
        Get the settings for the authenticated buyer.
        """
        try:
            buyer = Buyer.objects.get(user=request.user)
            settings = {
                "is_premium_customer": buyer.is_premium_customer,
                "preferred_payment_method": buyer.preferred_payment_method,
                "user_type": buyer.user.user_type,
                "is_active": buyer.user.is_active,
                "is_verified": buyer.user.is_verified
            }
            logger.info(f"Buyer settings retrieved: {settings}")
            return Response(settings)
        except Buyer.DoesNotExist:
            logger.warning(f"Buyer not found for user: {request.user.mobile_no}")
            return Response(
                {"error": "Buyer not found"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @extend_schema(
        summary="Update buyer settings",
        description="Update the settings for the authenticated buyer.",
        request=OpenApiTypes.OBJECT,
        responses={
            200: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
        },
        tags=["Buyer Management"]
    )
    @action(detail=False, methods=['put'], url_path='settings')
    def update_settings(self, request):
        """
        Update the settings for the authenticated buyer.
        """
        try:
            buyer = Buyer.objects.get(user=request.user)
            
            # Update buyer-specific fields
            if 'is_premium_customer' in request.data:
                buyer.is_premium_customer = request.data['is_premium_customer']
            
            if 'preferred_payment_method' in request.data:
                buyer.preferred_payment_method = request.data['preferred_payment_method']
            
            buyer.save()
            
            # Update user fields if provided
            if 'user_type' in request.data:
                buyer.user.user_type = request.data['user_type']
                buyer.user.save()
            
            logger.info(f"Buyer settings updated: {buyer.user.get_full_name()}")
            return Response(self.get_serializer(buyer).data)
            
        except Buyer.DoesNotExist:
            logger.warning(f"Buyer not found for user: {request.user.mobile_no}")
            return Response(
                {"error": "Buyer not found"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @extend_schema(
        summary="Get buyer referral code",
        description="Retrieve the referral code for the authenticated buyer.",
        responses={
            200: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
        },
        tags=["Buyer Management"]
    )
    @action(detail=False, methods=['get'], url_path='referral-code')
    def get_referral_code(self, request):
        """
        Get the referral code for the authenticated buyer.
        """
        try:
            buyer = Buyer.objects.get(user=request.user)
            # Generate a referral code based on buyer ID
            referral_code = f"REF{buyer.buyer_id.hex[:8].upper()}"
            logger.info(f"Buyer referral code retrieved: {referral_code}")
            return Response({"referral_code": referral_code})
        except Buyer.DoesNotExist:
            logger.warning(f"Buyer not found for user: {request.user.mobile_no}")
            return Response(
                {"error": "Buyer not found"},
                status=status.HTTP_404_NOT_FOUND
            )


@extend_schema_view(
    list=extend_schema(
        summary="List all Buyer Shipping Addresses",
        description="Returns a paginated list of all Buyer Shipping Addresses in the system with optional filtering.",
        parameters=[
            OpenApiParameter(
                name="buyer",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Filter shipping addresses by buyer ID",
                required=False
            ),
            OpenApiParameter(
                name="is_default",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="Filter by default address status",
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
                            "id": 1,
                            "buyer": 1,
                            "address1": "123 Main St",
                            "address2": "Apt 4B",
                            "barangay": 1,
                            "city": 1,
                            "province": 1,
                            "region": 1,
                            "country": 1,
                            "zip_code": "1234",
                            "is_default": True,
                            "created_at": "2025-08-31T17:00:00Z",
                            "updated_at": "2025-08-31T17:00:00Z"
                        }
                    ]
                }
            )
        ],
        tags=["Buyer Shipping Address Management"]
    ),
    create=extend_schema(
        summary="Create a new Buyer Shipping Address",
        description="Create a new Buyer Shipping Address entry.",
        request=BuyerShippingAddressSerializer,
        responses={
            201: BuyerShippingAddressSerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                'Create Shipping Address Request',
                value={
                    "buyer": 1,
                    "address1": "123 Main St",
                    "address2": "Apt 4B",
                    "barangay": 1,
                    "city": 1,
                    "province": 1,
                    "region": 1,
                    "country": 1,
                    "zip_code": "1234",
                    "is_default": True
                }
            )
        ],
        tags=["Buyer Shipping Address Management"]
    ),
    retrieve=extend_schema(
        summary="Get Buyer Shipping Address details",
        description="Retrieve detailed information for a specific Buyer Shipping Address.",
        responses={
            200: BuyerShippingAddressSerializer,
            404: OpenApiTypes.OBJECT,
        },
        tags=["Buyer Shipping Address Management"]
    ),
    update=extend_schema(
        summary="Update Buyer Shipping Address information",
        description="Update Buyer Shipping Address information.",
        request=BuyerShippingAddressSerializer,
        responses={
            200: BuyerShippingAddressSerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        tags=["Buyer Shipping Address Management"]
    ),
    partial_update=extend_schema(
        summary="Partially update Buyer Shipping Address information",
        description="Partially update Buyer Shipping Address information.",
        request=BuyerShippingAddressSerializer,
        responses={
            200: BuyerShippingAddressSerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        tags=["Buyer Shipping Address Management"]
    ),
    destroy=extend_schema(
        summary="Delete Buyer Shipping Address",
        description="Delete a Buyer Shipping Address entry.",
        responses={
            204: None,
            404: OpenApiTypes.OBJECT,
        },
        tags=["Buyer Shipping Address Management"]
    ),
)
class BuyerShippingAddressViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Buyer Shipping Address entities.

    Provides CRUD operations for Buyer Shipping Address entities including:
    - List all shipping addresses with filtering options
    - Create new shipping address entries
    - Retrieve shipping address details
    - Update shipping address information
    - Delete shipping address entries
    """
    queryset = BuyerShippingAddress.objects.select_related('buyer__user', 'barangay', 'city', 'province', 'region', 'country').all()
    serializer_class = BuyerShippingAddressSerializer
    lookup_field = 'id'

    def get_queryset(self):
        """
        Custom queryset with optional filtering.
        """
        queryset = BuyerShippingAddress.objects.select_related('buyer__user', 'barangay', 'city', 'province', 'region', 'country').all()

        # Filter by buyer
        buyer = self.request.query_params.get('buyer', None)
        if buyer:
            queryset = queryset.filter(buyer_id=buyer)

        # Filter by default status
        is_default = self.request.query_params.get('is_default', None)
        if is_default is not None:
            is_default_bool = is_default.lower() == 'true'
            queryset = queryset.filter(is_default=is_default_bool)

        user_info = self.request.user.get_full_name() or self.request.user.mobile_no
        logger.info(f"BuyerShippingAddress queryset filtered: {queryset.count()} results by user: {user_info}")
        return queryset

    def perform_create(self, serializer):
        """
        Custom create logic with logging.
        """
        shipping_address = serializer.save()
        user_info = self.request.user.get_full_name() or self.request.user.mobile_no
        logger.info(f"New shipping address created: {shipping_address.id} - {shipping_address.address1} by user: {user_info}")
        return shipping_address

    def perform_update(self, serializer):
        """
        Custom update logic with logging.
        """
        shipping_address = serializer.save()
        user_info = self.request.user.get_full_name() or self.request.user.mobile_no
        logger.info(f"Shipping address updated: {shipping_address.id} - {shipping_address.address1} by user: {user_info}")
        return shipping_address

    def perform_destroy(self, instance):
        """
        Custom delete logic with logging.
        """
        address_info = instance.address1
        address_id = instance.id
        user_info = self.request.user.get_full_name() or self.request.user.mobile_no
        instance.delete()
        logger.info(f"Shipping address deleted: {address_id} - {address_info} by user: {user_info}")

    @extend_schema(
        summary="Get buyer shipping addresses",
        description="Retrieve all shipping addresses for the authenticated buyer.",
        responses={
            200: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        tags=["Buyer Shipping Address Management"]
    )
    @action(detail=False, methods=['get'], url_path='my-addresses')
    def my_addresses(self, request):
        """
        Get all shipping addresses for the authenticated buyer.
        """
        try:
            buyer = Buyer.objects.get(user=request.user)
            shipping_addresses = BuyerShippingAddress.objects.filter(buyer=buyer)
            serializer = self.get_serializer(shipping_addresses, many=True)
            
            user_info = self.request.user.get_full_name() or self.request.user.mobile_no
            logger.info(f"Shipping addresses retrieved for buyer: {buyer.user.get_full_name()} by user: {user_info}")
            return Response({
                "buyer": buyer.user.get_full_name(),
                "shipping_addresses": serializer.data
            })

        except Buyer.DoesNotExist:
            user_info = self.request.user.get_full_name() or self.request.user.mobile_no
            logger.warning(f"Buyer not found for user: {request.user.mobile_no} by user: {user_info}")
            return Response(
                {"error": "Buyer not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    @extend_schema(
        summary="Set default shipping address",
        description="Set a shipping address as the default for the buyer.",
        request=OpenApiTypes.OBJECT,
        responses={
            200: BuyerShippingAddressSerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                'Set Default Request',
                value={
                    "is_default": True
                }
            )
        ],
        tags=["Buyer Shipping Address Management"]
    )
    @action(detail=True, methods=['patch'], url_path='set-default')
    def set_default(self, request, id=None):
        """
        Set a shipping address as the default for the buyer.
        """
        try:
            shipping_address = self.get_object()
            
            # Set all other addresses to non-default
            BuyerShippingAddress.objects.filter(buyer=shipping_address.buyer).update(is_default=False)
            
            # Set this address as default
            shipping_address.is_default = True
            shipping_address.save()
            
            serializer = self.get_serializer(shipping_address)
            user_info = self.request.user.get_full_name() or self.request.user.mobile_no
            logger.info(f"Default shipping address set: {shipping_address.id} - {shipping_address.address1} by user: {user_info}")
            return Response(serializer.data)

        except BuyerShippingAddress.DoesNotExist:
            user_info = self.request.user.get_full_name() or self.request.user.mobile_no
            logger.warning(f"Shipping address not found by user: {user_info}")
            return Response(
                {"error": "Shipping address not found"},
                status=status.HTTP_404_NOT_FOUND
            )


@extend_schema_view(
    list=extend_schema(
        summary="List all Buyer Payment Methods",
        description="Returns a paginated list of all Buyer Payment Methods in the system with optional filtering.",
        parameters=[
            OpenApiParameter(
                name="buyer",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Filter payment methods by buyer ID",
                required=False
            ),
            OpenApiParameter(
                name="payment_type",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by payment type",
                required=False
            ),
            OpenApiParameter(
                name="is_default",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="Filter by default payment method status",
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
                            "id": 1,
                            "buyer": 1,
                            "payment_type": "gcash",
                            "account_number": "09123456789",
                            "account_name": "John Doe",
                            "is_default": True,
                            "created_at": "2025-08-31T17:00:00Z",
                            "updated_at": "2025-08-31T17:00:00Z"
                        }
                    ]
                }
            )
        ],
        tags=["Buyer Payment Method Management"]
    ),
    create=extend_schema(
        summary="Create a new Buyer Payment Method",
        description="Create a new Buyer Payment Method entry.",
        request=BuyerPaymentMethodSerializer,
        responses={
            201: BuyerPaymentMethodSerializer,
            400: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                'Create Payment Method Request',
                value={
                    "buyer": 1,
                    "payment_type": "gcash",
                    "account_number": "09123456789",
                    "account_name": "John Doe",
                    "is_default": True
                }
            )
        ],
        tags=["Buyer Payment Method Management"]
    ),
    retrieve=extend_schema(
        summary="Get Buyer Payment Method details",
        description="Retrieve detailed information for a specific Buyer Payment Method.",
        responses={
            200: BuyerPaymentMethodSerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        tags=["Buyer Payment Method Management"]
    ),
    update=extend_schema(
        summary="Update Buyer Payment Method information",
        description="Update Buyer Payment Method information.",
        request=BuyerPaymentMethodSerializer,
        responses={
            200: BuyerPaymentMethodSerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        tags=["Buyer Payment Method Management"]
    ),
    partial_update=extend_schema(
        summary="Partially update Buyer Payment Method information",
        description="Partially update Buyer Payment Method information.",
        request=BuyerPaymentMethodSerializer,
        responses={
            200: BuyerPaymentMethodSerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        tags=["Buyer Payment Method Management"]
    ),
    destroy=extend_schema(
        summary="Delete Buyer Payment Method",
        description="Delete a Buyer Payment Method entry.",
        responses={
            204: None,
            404: OpenApiTypes.OBJECT,
        },
        tags=["Buyer Payment Method Management"]
    ),
)
class BuyerPaymentMethodViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Buyer Payment Method entities.

    Provides CRUD operations for Buyer Payment Method entities including:
    - List all payment methods with filtering options
    - Create new payment method entries
    - Retrieve payment method details
    - Update payment method information
    - Delete payment method entries
    """
    queryset = BuyerPaymentMethod.objects.select_related('buyer__user').all()
    serializer_class = BuyerPaymentMethodSerializer
    lookup_field = 'id'

    def get_queryset(self):
        """
        Custom queryset with optional filtering.
        """
        queryset = BuyerPaymentMethod.objects.select_related('buyer__user').all()

        # Filter by buyer
        buyer = self.request.query_params.get('buyer', None)
        if buyer:
            queryset = queryset.filter(buyer_id=buyer)

        # Filter by payment type
        payment_type = self.request.query_params.get('payment_type', None)
        if payment_type:
            queryset = queryset.filter(payment_type__icontains=payment_type)

        # Filter by default status
        is_default = self.request.query_params.get('is_default', None)
        if is_default is not None:
            is_default_bool = is_default.lower() == 'true'
            queryset = queryset.filter(is_default=is_default_bool)

        user_info = self.request.user.get_full_name() or self.request.user.mobile_no
        logger.info(f"BuyerPaymentMethod queryset filtered: {queryset.count()} results by user: {user_info}")
        return queryset

    def perform_create(self, serializer):
        """
        Custom create logic with logging.
        """
        payment_method = serializer.save()
        user_info = self.request.user.get_full_name() or self.request.user.mobile_no
        logger.info(f"New payment method created: {payment_method.id} - {payment_method.payment_type} by user: {user_info}")
        return payment_method

    def perform_update(self, serializer):
        """
        Custom update logic with logging.
        """
        payment_method = serializer.save()
        user_info = self.request.user.get_full_name() or self.request.user.mobile_no
        logger.info(f"Payment method updated: {payment_method.id} - {payment_method.payment_type} by user: {user_info}")
        return payment_method

    def perform_destroy(self, instance):
        """
        Custom delete logic with logging.
        """
        payment_info = instance.payment_type
        payment_id = instance.id
        user_info = self.request.user.get_full_name() or self.request.user.mobile_no
        instance.delete()
        logger.info(f"Payment method deleted: {payment_id} - {payment_info} by user: {user_info}")

    @extend_schema(
        summary="Get buyer payment methods",
        description="Retrieve all payment methods for the authenticated buyer.",
        responses={
            200: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        tags=["Buyer Payment Method Management"]
    )
    @action(detail=False, methods=['get'], url_path='my-payment-methods')
    def my_payment_methods(self, request):
        """
        Get all payment methods for the authenticated buyer.
        """
        try:
            buyer = Buyer.objects.get(user=request.user)
            payment_methods = BuyerPaymentMethod.objects.filter(buyer_id=buyer)
            serializer = self.get_serializer(payment_methods, many=True)
            
            user_info = self.request.user.get_full_name() or self.request.user.mobile_no
            logger.info(f"Payment methods retrieved for buyer: {buyer.user.get_full_name()} by user: {user_info}")
            return Response({
                "buyer": buyer.user.get_full_name(),
                "payment_methods": serializer.data
            })

        except Buyer.DoesNotExist:
            user_info = self.request.user.get_full_name() or self.request.user.mobile_no
            logger.warning(f"Buyer not found for user: {request.user.mobile_no} by user: {user_info}")
            return Response(
                {"error": "Buyer not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    @extend_schema(
        summary="Set default payment method",
        description="Set a payment method as the default for the buyer.",
        request=OpenApiTypes.OBJECT,
        responses={
            200: BuyerPaymentMethodSerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                'Set Default Request',
                value={
                    "is_default": True
                }
            )
        ],
        tags=["Buyer Payment Method Management"]
    )
    @action(detail=True, methods=['patch'], url_path='set-default')
    def set_default(self, request, id=None):
        """
        Set a payment method as the default for the buyer.
        """
        try:
            payment_method = self.get_object()
            
            # Set all other payment methods to non-default
            BuyerPaymentMethod.objects.filter(buyer=payment_method.buyer).update(is_default=False)
            
            # Set this payment method as default
            payment_method.is_default = True
            payment_method.save()
            
            serializer = self.get_serializer(payment_method)
            user_info = self.request.user.get_full_name() or self.request.user.mobile_no
            logger.info(f"Default payment method set: {payment_method.id} - {payment_method.payment_type} by user: {user_info}")
            return Response(serializer.data)

        except BuyerPaymentMethod.DoesNotExist:
            user_info = self.request.user.get_full_name() or self.request.user.mobile_no
            logger.warning(f"Payment method not found by user: {user_info}")
            return Response(
                {"error": "Payment method not found"},
                status=status.HTTP_404_NOT_FOUND
            )
