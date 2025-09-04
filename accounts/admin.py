from django.contrib import admin

from .models import CustomUser, Buyer, Seller, BuyerShippingAddress, BuyerPaymentMethod, Shop, Region, Province, City, Barangay, Country

admin.site.register(CustomUser)
admin.site.register(Buyer)
admin.site.register(Seller)
admin.site.register(BuyerShippingAddress)
admin.site.register(BuyerPaymentMethod)
admin.site.register(Shop)
admin.site.register(Region)
admin.site.register(Province)
admin.site.register(City)
admin.site.register(Barangay)
admin.site.register(Country)
