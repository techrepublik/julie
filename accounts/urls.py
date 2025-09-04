"""
URL configuration for accounts app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.buyer_views import (
    BuyerViewSet,
    BuyerShippingAddressViewSet,
    BuyerPaymentMethodViewSet
)
from .views.seller_views import SellerViewSet
from .views.address_lookup_views import (
    CountryViewSet,
    RegionViewSet,
    ProvinceViewSet,
    CityViewSet,
    BarangayViewSet
)

# Create a router for the accounts app
router = DefaultRouter()
router.register(r'buyers', BuyerViewSet, basename='buyer')
router.register(r'buyer-shipping-addresses', BuyerShippingAddressViewSet, basename='buyer-shipping-address')
router.register(r'buyer-payment-methods', BuyerPaymentMethodViewSet, basename='buyer-payment-method')
router.register(r'sellers', SellerViewSet, basename='seller')
router.register(r'countries', CountryViewSet, basename='country')
router.register(r'regions', RegionViewSet, basename='region')
router.register(r'provinces', ProvinceViewSet, basename='province')
router.register(r'cities', CityViewSet, basename='city')
router.register(r'barangays', BarangayViewSet, basename='barangay')

app_name = 'accounts'

urlpatterns = [
    # Include the router URLs
    path('', include(router.urls)),
    
    # Additional custom URLs can be added here
    # path('custom-endpoint/', views.custom_view, name='custom_endpoint'),
]
