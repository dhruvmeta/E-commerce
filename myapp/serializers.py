from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
class USerializer(serializers.ModelSerializer):

    class Meta:
        model= User
        fields=['email','password','name','tc','is_seller']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'



class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = '__all__'


class cartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = cartItem
        fields = ['id','product','quantity']

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseProduct
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class CartSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)   # nested product details
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source="product", write_only=True
    )

    class Meta:
        model = cartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'user']
        read_only_fields = ['user']

class PurchaseProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseProduct
        fields = '__all__'