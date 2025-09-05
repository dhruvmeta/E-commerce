from django.contrib import admin
from myapp.models import *
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
 
admin.site.register(User)

class ProductAdmin(admin.ModelAdmin):
    model = Product
    list_display = ['id', 'name', 'price']
    fields=['id','name','description','category','price','stock','image','created_at','updated_at','user']
    readonly_fields=['created_at','updated_at','id'] 
admin.site.register(Product,ProductAdmin)

class ProductCategoryAdmin(admin.ModelAdmin):
        model = ProductCategory
        fields=['name','description','created_at','updated_at']
        readonly_fields=['created_at','updated_at']
admin.site.register(ProductCategory,ProductCategoryAdmin)

class cartItemAdmin(admin.ModelAdmin):
        model = cartItem
        list_display = ['id', 'user', 'product','quantity'] 
        fields=['user','product','quantity']
admin.site.register(cartItem,cartItemAdmin)

class PurchaseProductAdmin(admin.ModelAdmin):
        model = PurchaseProduct
        list_display = ['id', 'user', 'product','quantity','created_at','updated_at'] 
        fields=['user','product','quantity']
admin.site.register(PurchaseProduct,PurchaseProductAdmin)



class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'product','paid']
    fields=['user','razorpay_payment_id','razorpay_order_id','razorpay_signature','paid']
admin.site.register(Payment,PaymentAdmin)
