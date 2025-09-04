from django.shortcuts import render
from rest_framework import viewsets
from .models import CustomUser, Buyer, Seller, BuyerShippingAddress, BuyerPaymentMethod, Shop, Region, Province, City, Barangay, Country
from .serializers import CustomUserSerializer, BuyerSerializer, SellerSerializer, BuyerShippingAddressSerializer, BuyerPaymentMethodSerializer, ShopSerializer, RegionSerializer, ProvinceSerializer, CitySerializer, BarangaySerializer, CountrySerializer

# Create your views here.

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

class BuyerViewSet(viewsets.ModelViewSet):
    queryset = Buyer.objects.all()
    serializer_class = BuyerSerializer

class SellerViewSet(viewsets.ModelViewSet):
    queryset = Seller.objects.all()
    serializer_class = SellerSerializer

class BuyerShippingAddressViewSet(viewsets.ModelViewSet):
    queryset = BuyerShippingAddress.objects.all()
    serializer_class = BuyerShippingAddressSerializer

class BuyerPaymentMethodViewSet(viewsets.ModelViewSet):
    queryset = BuyerPaymentMethod.objects.all()
    serializer_class = BuyerPaymentMethodSerializer

class ShopViewSet(viewsets.ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer

class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer

class ProvinceViewSet(viewsets.ModelViewSet):
    queryset = Province.objects.all()
    serializer_class = ProvinceSerializer

class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer

class BarangayViewSet(viewsets.ModelViewSet):
    queryset = Barangay.objects.all()
    serializer_class = BarangaySerializer

class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer