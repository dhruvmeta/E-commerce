from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .serializers import *
from rest_framework.views import APIView
from .models import *
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework import permissions
from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import BasePermission
from django.contrib.auth.hashers import make_password
from .models import Notification
from django.core.mail import send_mail
from django.contrib.auth import authenticate
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
# razorpay 
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import razorpay
from django.conf import settings
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import hmac
import hashlib
import json


# notification
def create_notification(user, message):
    Notification.objects.create(user=user, message=message)

def index(request):
    return render(request, 'razorpay.html')

def loginview(request):
    return render(request, 'loginview.html')
#custom permission for seller

class IsSeller(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_seller

# Token generater
def get_tokens_for_user(user):
    if not user.is_active:
      raise AuthenticationFailed("User is not active")

    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class userregister(APIView):
    def post(self,request):
        serializers=UserSerializer(data=request.data)
        if serializers.is_valid():
            password=serializers.validated_data['password']
            # convert to hash 
            serializers.validated_data['password']=make_password(password)
            emp=serializers.save()
            sub ="Welcome!!!"
            msg =f"Dear User !\nYour Account has been created with us !\nEnjoy our service .\nif any query ,contact us at \nmetadhruv4@gmail.com | 7435820532"
            from_Email=settings.EMAIL_HOST_USER
            to_email=[emp.email]
            send_mail(subject=sub,message=msg,from_email=from_Email,recipient_list=to_email)
            token=get_tokens_for_user(emp)
            return Response({'token': token, 'data':serializers.data}, status=status.HTTP_201_CREATED)
        return Response(serializers.errors,status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        # user = User.objects.filter(email=email).first()

        # if user is None:
        #     raise AuthenticationFailed('User not found')

        # if not user.check_password(password):
        #     raise AuthenticationFailed('Incorrect password')
        
        # CHECK USER AUTHENCTICATE OR NOT 
        user = authenticate(email=email, password=password)
        if not user:
            raise AuthenticationFailed('User not found')
        serializer = UserSerializer(user)

        return Response({'token': get_tokens_for_user(user), 'data':serializer.data}, status=status.HTTP_200_OK)
    

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Get all refresh tokens for this user and blacklist them
            tokens = OutstandingToken.objects.filter(user=request.user)
            for token in tokens:
                BlacklistedToken.objects.get_or_create(token=token)

            return Response({"message": "User logged out successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(APIView):

    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        serializer = USerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request):
        user = request.user
        serializer = USerializer(user, data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        user = request.user
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class ProductView(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = cartItem.objects.filter(user=request.user)
        #data = [{"product": i.product, "quantity": i.quantity} for i in items]
        serializer=CartSerializer(items,many=True)
        return Response({"cart":serializer.data})

# Add product to cart
class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get("product")
        quantity = int(request.data.get("quantity", 1))  # default = 1

        if not product_id:
            return Response({"error": "Product ID is required"}, status=400)

        try:
            # Check if item already exists in cart
            cart_item = cartItem.objects.get(user=request.user, product_id=product_id)

            # If exists → update quantity
            cart_item.quantity += quantity
            cart_item.save()
            return Response({"message": "Product quantity updated in cart!"})

        except cartItem.DoesNotExist:
            # If not exists → create new cart item
            serializer = cartItemSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response({"message": "Product added to cart!"})
            return Response(serializer.errors, status=400)

class AddProductView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
       
        if not request.user.is_seller:
            return Response({"error": "Only sellers can add products."}, status=status.HTTP_403_FORBIDDEN)

        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # attach seller
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def get (sel,request):
        if not request.user.is_seller:
            return Response({"error": "Only sellers can do this."}, status=status.HTTP_403_FORBIDDEN)
        products = Product.objects.filter(user=request.user)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, pk):
        if not request.user.is_seller:
            return Response({"error": "Only sellers can do this."}, status=status.HTTP_403_FORBIDDEN)
        product = Product.objects.get(pk=pk,user=request.user)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def put (self, request, pk):
        if not request.user.is_seller:
            return Response({"error": "Only sellers can add products."}, status=status.HTTP_403_FORBIDDEN)
        product = Product.objects.get(pk=pk,user=request.user)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

class CreatePaymentLink(APIView):
    permission_classes = [IsAuthenticated]  # optional

    def post(self, request):
        data = request.data
        product_id = data.get("product_id")

        if not product_id:
            return Response({"error": "Product ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Get product details from DB
            product = Product.objects.get(id=product_id)

            # Amount in paise
            amount_paise = int(product.price) * 100

            # Create Razorpay payment link
            payment_link = client.payment_link.create({
                "amount": amount_paise,
                "currency": "INR",
                "accept_partial": False,
                "description": f"Payment for {product.name}",
                "customer": {
                    "name": request.user.name if hasattr(request.user, 'name') else request.user.username,
                    "email": request.user.email,
                    "contact": data.get("contact")  # still need user’s phone number
                },
                "notify": {
                    "sms": True,
                    "email": True
                },
                "reminder_enable": True,
                "callback_url": "https://s2xhcvq1-8000.inc1.devtunnels.ms/webhook/",
                "callback_method": "get",
                "notes": {"product_id": str(product.id)}
            })

            Payment.objects.create(
                user=request.user,
                product=product,
                amount=amount_paise,
                razorpay_order_id=payment_link["id"],  # link_id is used here
                paid=False
            )


            return Response(payment_link)

        except Product.DoesNotExist:
            return Response({"error": "Invalid product ID"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)  

@csrf_exempt
def razorpay_webhook(request):
    webhook_secret = 'test@123'
    print("🌐 Incoming Razorpay request")

    if request.method == "POST":  # Webhook call
        received_signature = request.headers.get("X-Razorpay-Signature")
        body = request.body

        if not received_signature:
            return JsonResponse({"error": "Signature missing in header"}, status=400)

        generated_signature = hmac.new(
            bytes(webhook_secret, "utf-8"),
            body,
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(received_signature, generated_signature):
            return JsonResponse({"error": "Invalid signature"}, status=400)

        event = json.loads(body)

        if event["event"] == "payment_link.paid":
            payment_id = event["payload"]["payment"]["entity"]["id"]
            link_id = event["payload"]["payment_link"]["entity"]["id"]

            try:
                payment = Payment.objects.get(razorpay_order_id=link_id)
                payment.razorpay_payment_id = payment_id
                payment.razorpay_signature = received_signature   # store signature
                payment.paid = True
                payment.save()

                #  aggregate purchases instead of creating new rows
                purchase, created = PurchaseProduct.objects.get_or_create(
                    user=payment.user,
                    product=payment.product,
                    defaults={
                        "quantity": 1,
                        "amount": payment.product.price
                    }
                )
                if not created:
                    purchase.quantity += 1
                    purchase.amount += payment.product.price
                    purchase.save()

                print(f" Payment successful & purchase stored for {payment.user.email}")
            except Payment.DoesNotExist:
                print("❌ Payment entry not found for link_id:", link_id)

        return JsonResponse({"status": "ok"}, status=200)

    elif request.method == "GET":  # Callback redirect from Razorpay checkout
        payment_id = request.GET.get("razorpay_payment_id")
        link_id = request.GET.get("razorpay_payment_link_id")
        received_signature = request.GET.get("razorpay_signature")

        if not (payment_id and link_id and received_signature):
            return JsonResponse({"error": "Missing params in callback"}, status=400)

        try:
            payment = Payment.objects.get(razorpay_order_id=link_id)
            payment.razorpay_payment_id = payment_id
            payment.razorpay_signature = received_signature   #  store signature
            payment.paid = True
            payment.save()

            #  aggregate purchases instead of creating new rows
            purchase, created = PurchaseProduct.objects.get_or_create(
                user=payment.user,
                product=payment.product,
                defaults={
                    "quantity": 1,
                    "amount": payment.product.price
                }
            )
            if not created:
                purchase.quantity += 1
                purchase.amount += payment.product.price
                purchase.save()

            print(f" Payment successful via callback for {payment.user.email}")
        except Payment.DoesNotExist:
            print("❌ Payment entry not found for link_id:", link_id)

        return JsonResponse({"status": "callback success"}, status=200)

    return JsonResponse({"error": "Invalid method"}, status=405)
    
class PaymentCallback(APIView):
    def get(self, request):
        payment_id = request.GET.get("razorpay_payment_id")
        payment_link_id = request.GET.get("razorpay_payment_link_id")
        status = request.GET.get("razorpay_payment_link_status")
        signature = request.GET.get("razorpay_signature")

        try:
            client.utility.verify_payment_link_signature({
                "razorpay_payment_id": payment_id,
                "razorpay_payment_link_id": payment_link_id,
                "razorpay_payment_link_status": status,
                "razorpay_signature": signature
            })
            return Response({"message": "Payment verified successfully", "status": status})
        except Exception as e:
            return Response({"error": str(e)}, status=400)
        
class PurchaseView(APIView):
    def get(self, request):
        user = request.user
        purchases = PurchaseProduct.objects.filter(user=user)
        serializer = PurchaseProductSerializer(purchases, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserLoginStatsView(APIView):
    def get(self, request):
        users = User.objects.all()
        logged_in_count = 0
        logged_out_count = 0

        for user in users:
            tokens = OutstandingToken.objects.filter(user=user)
            has_active_token = False
            for token in tokens:
                if not BlacklistedToken.objects.filter(token=token).exists():
                    has_active_token = True
                    break
            if has_active_token:
                logged_in_count += 1
            else:
                logged_out_count += 1

        return Response({
            "logged_in_users": logged_in_count,
            "logged_out_users": logged_out_count
        })