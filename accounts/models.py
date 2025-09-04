from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

import uuid
import random

import logging

logger = logging.getLogger(__name__)


SEX_CHOICES = (
    ('male', 'Male'),
    ('female', 'Female'),
)

USER_TYPE_CHOICES = (
    ('superadmin', 'Super Admin'),
    ('admin', 'Admin'),
    ('seller', 'Seller'),
    ('buyer', 'Buyer'),
)

PAYMENT_METHOD_CHOICES = (
    ('gcash', 'Gcash'),
    ('paymaya', 'Paymaya'),
    ('bank_card', 'Bank Card'),
    ('cash_on_delivery', 'Cash on Delivery'),
)

BANK_CARD_TYPE_CHOICES = (
    ('visa', 'Visa'),
    ('mastercard', 'Mastercard'),
    ('american_express', 'American Express'),
)

SHOP_TYPE_CHOICES = (
    ('water', 'Water'),
    ('laundry', 'Laundry'),
    ('rice', 'Rice'),
    ('groceries', 'Groceries'),
    ('other', 'Other'),
)

def user_pic_upload_path(instance, filename):
    """Upload path with random filename for user pictures"""
    return f'user_pics/{random_filename(instance, filename)}'

def random_filename(instance, filename):
    """Generate a random filename for the uploaded file"""
    return f'{uuid.uuid4()}_{filename}'

def product_pic_upload_path(instance, filename):
    """Upload path with random filename for product pictures"""
    return f'product_pics/{instance.shop.shop_id}/{random_filename(instance, filename)}'

def shop_pic_upload_path(instance, filename):
    """Upload path with random filename for shop pictures"""
    return f'shop_pics/{instance.shop_id}/{random_filename(instance, filename)}'

class Country(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class Region(models.Model):
    name = models.CharField(max_length=255)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
class Province(models.Model):
    name = models.CharField(max_length=255)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
class City(models.Model):
    name = models.CharField(max_length=255)
    province = models.ForeignKey(Province, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
class Barangay(models.Model):
    name = models.CharField(max_length=255)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

# Custom User Manager
logger.info("Custom User Manager")

class CustomUserManager(BaseUserManager):
    def create_user(self, mobile_no, password=None, **extra_fields):
        if not mobile_no:
            raise ValueError("The Mobile Number must be set")
        
        if mobile_no.isdigit() == False:
            raise ValueError("The Mobile Number must be a number")
        
        if mobile_no.startswith('0') == False:
            raise ValueError("The Mobile Number must start with 0")
        
        if len(mobile_no) != 11:
            raise ValueError("The Mobile Number must be 11 digits")
        
        if not password:
            raise ValueError("The Password must be set")
        
        user = self.model(mobile_no=mobile_no, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

        return user

    def create_superuser(self, mobile_no, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(mobile_no, password, **extra_fields)

# Custom User Models
logger.info("Custom User Models")


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model for the application.
    """
    user_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    mobile_no = models.CharField(max_length=15, unique=True)
    address1 = models.TextField(blank=True, null=True)
    address2 = models.TextField(blank=True, null=True)
    barangay = models.ForeignKey(Barangay, on_delete=models.CASCADE, blank=True, null=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, blank=True, null=True)
    province = models.ForeignKey(Province, on_delete=models.CASCADE, blank=True, null=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, blank=True, null=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, blank=True, null=True)
    zip_code = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True) 
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    sex = models.CharField(max_length=10, choices=SEX_CHOICES, default='male')
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='buyer')
    picture = models.ImageField(upload_to=user_pic_upload_path, blank=True, null=True)
    token = models.CharField(max_length=255, blank=True, null=True)
    token_expiry = models.DateTimeField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(auto_now_add=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'mobile_no'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at', 'last_name', 'first_name']
        indexes = [
            models.Index(fields=['mobile_no']),
        ]

    def __str__(self):
        return self.mobile_no
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_short_name(self):
        return self.first_name
    
    
    def get_mobile_no(self):
        return self.mobile_no

# Seller Models
logger.info(f"{__name__} Seller Models")
    
class Seller(models.Model):
    seller_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    is_free_plan = models.BooleanField(default=False)
    is_premium_plan = models.BooleanField(default=False)
    is_premium_plan_expiry = models.DateField(blank=True, null=True)
    is_premium_plan_image = models.ImageField(upload_to=shop_pic_upload_path, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.user.mobile_no
    
    class Meta:
        verbose_name = 'Seller'
        verbose_name_plural = 'Sellers'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['seller_id']),
        ]


# Buyer Models
logger.info(f"{__name__} Buyer Models")

class Buyer(models.Model):
    buyer_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    is_premium_customer = models.BooleanField(default=False)
    is_premium_customer_expiry = models.DateField(blank=True, null=True)
    preferred_payment_method = models.CharField(max_length=255, choices=PAYMENT_METHOD_CHOICES, default='gcash')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.user.get_full_name()
    
    class Meta:
        verbose_name = 'Buyer'
        verbose_name_plural = 'Buyers'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['buyer_id']),
        ]

# Shop Models
logger.info(f"{__name__} Shop Models")

class Shop(models.Model):
    shop_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    shop_type = models.CharField(max_length=10, choices=SHOP_TYPE_CHOICES, default='water')
    shop_name = models.CharField(max_length=255, blank=True, null=True)
    shop_short_name = models.CharField(max_length=255, blank=True, null=True)
    shop_address1 = models.TextField(blank=True, null=True)
    shop_address2 = models.TextField(blank=True, null=True)
    shop_barangay = models.ForeignKey(Barangay, on_delete=models.CASCADE, blank=True, null=True)
    shop_city = models.ForeignKey(City, on_delete=models.CASCADE, blank=True, null=True)
    shop_province = models.ForeignKey(Province, on_delete=models.CASCADE, blank=True, null=True)
    shop_region = models.ForeignKey(Region, on_delete=models.CASCADE, blank=True, null=True)
    shop_country = models.ForeignKey(Country, on_delete=models.CASCADE, blank=True, null=True)
    shop_zip_code = models.CharField(max_length=255, blank=True, null=True)
    shop_contact_number = models.CharField(max_length=255, blank=True, null=True)
    shop_contact_person = models.CharField(max_length=255, blank=True, null=True)
    shop_contact_person_number = models.CharField(max_length=255, blank=True, null=True)
    shop_email = models.EmailField(max_length=255, blank=True, null=True)
    shop_website = models.URLField(blank=True, null=True)
    shop_facebook = models.URLField(blank=True, null=True)
    shop_instagram = models.URLField(blank=True, null=True)
    shop_youtube = models.URLField(blank=True, null=True)
    shop_tiktok = models.URLField(blank=True, null=True)
    bank_name = models.CharField(max_length=255, blank=True, null=True)
    bank_account_number = models.CharField(max_length=255, blank=True, null=True)
    bank_account_name = models.CharField(max_length=255, blank=True, null=True)
    geolocation = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    google_maps_url = models.URLField(blank=True, null=True)
    google_maps_image = models.ImageField(upload_to=shop_pic_upload_path, blank=True, null=True)
    shop_picture1 = models.ImageField(upload_to=shop_pic_upload_path, blank=True, null=True)
    shop_picture2 = models.ImageField(upload_to=shop_pic_upload_path, blank=True, null=True)
    shop_picture3 = models.ImageField(upload_to=shop_pic_upload_path, blank=True, null=True)
    shop_business_permit_number = models.CharField(max_length=255, blank=True, null=True)
    shop_business_permit_expiry = models.DateField(blank=True, null=True)
    shop_business_permit_image = models.ImageField(upload_to=shop_pic_upload_path, blank=True, null=True)
    shop_dti_permit_number = models.CharField(max_length=255, blank=True, null=True)
    shop_dti_permit_expiry = models.DateField(blank=True, null=True)
    shop_dti_permit_image = models.ImageField(upload_to=shop_pic_upload_path, blank=True, null=True)
    is_philgeps_registered = models.BooleanField(default=False)
    philgeps_permit_number = models.CharField(max_length=255, blank=True, null=True)
    philgeps_permit_expiry = models.DateField(blank=True, null=True)
    philgeps_permit_image = models.ImageField(upload_to=shop_pic_upload_path, blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Shop'
        verbose_name_plural = 'Shops'
        ordering = ['-created_at', 'shop_short_name']
        indexes = [
            models.Index(fields=['shop_id']),
        ]

    def __str__(self):
        return self.shop_short_name
    
    def get_geo_location(self):
        if self.geolocation:
            return self.geolocation
        else:
            return f"{self.shop_city.name}, {self.shop_province.name}, {self.shop_region.name}, {self.shop_country.name}"

    def get_long_lat(self):
        if self.latitude and self.longitude:
            return f"{self.latitude}, {self.longitude}"
        else:
            return None
        
    def get_google_maps_url(self):
        if self.google_maps_url:
            return self.google_maps_url
        else:
            return None
        
    def get_google_maps_image(self):
        if self.google_maps_image:
            return self.google_maps_image
        else:
            return None
    

# Buyer Models
logger.info("Buyer Shipping Address Models")

class BuyerShippingAddress(models.Model):
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE)
    address1 = models.TextField(blank=True, null=True)
    address2 = models.TextField(blank=True, null=True)
    barangay = models.ForeignKey(Barangay, on_delete=models.CASCADE, blank=True, null=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, blank=True, null=True)
    province = models.ForeignKey(Province, on_delete=models.CASCADE, blank=True, null=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, blank=True, null=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, blank=True, null=True)
    zip_code = models.CharField(max_length=255, blank=True, null=True)
    geolocation = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    google_maps_url = models.URLField(blank=True, null=True)
    google_maps_image = models.ImageField(upload_to=shop_pic_upload_path, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Buyer Shipping Address'
        verbose_name_plural = 'Buyer Shipping Addresses'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['id']),
        ]

    def __str__(self):
        return self.buyer.user.get_full_name()
    


# Buyer Payment Method Models
logger.info("Buyer Payment Method Models")

class BuyerPaymentMethod(models.Model):
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=255, choices=PAYMENT_METHOD_CHOICES, default='gcash')
    payment_method_details = models.JSONField(blank=True, null=True)
    bank_card_type = models.CharField(max_length=255, choices=BANK_CARD_TYPE_CHOICES, blank=True, null=True)
    bank_card_brand = models.CharField(max_length=255, blank=True, null=True)
    bank_card_last4 = models.CharField(max_length=4, blank=True, null=True)
    bank_card_exp_month = models.CharField(max_length=2, blank=True, null=True)
    bank_card_exp_year = models.CharField(max_length=4, blank=True, null=True)
    bank_card_name = models.CharField(max_length=255, blank=True, null=True)
    bank_card_number = models.CharField(max_length=16, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Buyer Payment Method'
        verbose_name_plural = 'Buyer Payment Methods'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['id']),
        ]

    def __str__(self):
        return self.buyer.user.get_full_name()