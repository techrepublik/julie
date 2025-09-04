from rest_framework import serializers
from .models import CustomUser, Buyer, Seller, BuyerShippingAddress, BuyerPaymentMethod, Shop, Region, Province, City, Barangay, Country

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = '__all__'

class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = '__all__'

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'

class BarangaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Barangay
        fields = '__all__'

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'

class CustomUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    barangay = serializers.PrimaryKeyRelatedField(queryset=Barangay.objects.all(), required=False, allow_null=True)
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all(), required=False, allow_null=True)
    province = serializers.PrimaryKeyRelatedField(queryset=Province.objects.all(), required=False, allow_null=True)
    region = serializers.PrimaryKeyRelatedField(queryset=Region.objects.all(), required=False, allow_null=True)
    country = serializers.PrimaryKeyRelatedField(queryset=Country.objects.all(), required=False, allow_null=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'mobile_no', 'first_name', 'last_name', 'email', 'password',
            'user_type', 'address1', 'address2', 'barangay', 'city', 'province', 'region', 'country', 'zip_code'
        ]
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user

class CustomUserSerializer(serializers.ModelSerializer):
    barangay = BarangaySerializer()
    city = CitySerializer()
    province = ProvinceSerializer()
    region = RegionSerializer()
    country = CountrySerializer()
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['barangay'] = BarangaySerializer(instance.barangay).data
        data['city'] = CitySerializer(instance.city).data
        data['province'] = ProvinceSerializer(instance.province).data
        data['region'] = RegionSerializer(instance.region).data
        data['country'] = CountrySerializer(instance.country).data
        return data
    
    class Meta:
        model = CustomUser
        fields = [
            'user_id', 'mobile_no', 'first_name', 'last_name', 'email',
            'user_type', 'address1', 'address2', 'barangay', 'city', 'province', 'region', 'country', 'zip_code',
            'is_active', 'is_staff', 'is_verified', 'date_joined',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user_id', 'date_joined', 'created_at', 'updated_at']

class BuyerSerializer(serializers.ModelSerializer):
    user = CustomUserCreateSerializer()

    class Meta:
        model = Buyer
        fields = [
            'buyer_id', 'user', 'is_premium_customer', 'preferred_payment_method',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['buyer_id', 'created_at', 'updated_at']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        # Extract password and mobile_no for create_user method
        password = user_data.pop('password')
        mobile_no = user_data.pop('mobile_no')
        # Create the user first
        user = CustomUser.objects.create_user(mobile_no=mobile_no, password=password, **user_data)
        # Create the buyer with the user
        buyer = Buyer.objects.create(user=user, **validated_data)
        return buyer
    
    def update(self, instance, validated_data):
        if 'user' in validated_data:
            user_data = validated_data.pop('user')
            user = instance.user
            # Update user fields
            for field, value in user_data.items():
                if field == 'password':
                    user.set_password(value)
                else:
                    setattr(user, field, value)
            user.save()

        # Update buyer fields
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user'] = CustomUserSerializer(instance.user).data
        return data

class ShopCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating shops during seller creation.
    Excludes seller field as it will be set automatically.
    """
    class Meta:
        model = Shop
        exclude = ['seller', 'shop_id', 'created_at', 'updated_at']

class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = '__all__'

class SellerSerializer(serializers.ModelSerializer):
    user = CustomUserCreateSerializer()
    shop = ShopCreateSerializer(required=False)  # Make shop optional for creation

    class Meta:
        model = Seller
        fields = [
            'seller_id', 'user', 'shop', 'is_free_plan', 'is_premium_plan', 
            'is_premium_plan_expiry', 'is_premium_plan_image',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['seller_id', 'created_at', 'updated_at']    

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        password = user_data.pop('password')
        mobile_no = user_data.pop('mobile_no')
        user = CustomUser.objects.create_user(mobile_no=mobile_no, password=password, **user_data)
        
        # Create seller first
        seller = Seller.objects.create(user=user, **validated_data)
        
        # Create shop if provided
        if 'shop' in validated_data:
            shop_data = validated_data.pop('shop')
            shop = Shop.objects.create(seller=seller, **shop_data)
        
        return seller
    
    def update(self, instance, validated_data):
        if 'user' in validated_data:
            user_data = validated_data.pop('user')
            user = instance.user
            for field, value in user_data.items():
                if field == 'password':
                    user.set_password(value)
                else:
                    setattr(user, field, value)
            user.save()

        # Update seller fields
        for field, value in validated_data.items():
            if field != 'shop':  # Skip shop field in update
                setattr(instance, field, value)
        instance.save()
        return instance
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user'] = CustomUserSerializer(instance.user).data
        
        # Get shop data if it exists
        try:
            shop = Shop.objects.get(seller=instance)
            data['shop'] = ShopSerializer(shop).data
        except Shop.DoesNotExist:
            data['shop'] = None
        
        return data

class BuyerShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuyerShippingAddress
        fields = '__all__'

class BuyerPaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuyerPaymentMethod
        fields = '__all__'


