from django.urls import path
from .views import *
from myapp import views
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView




urlpatterns = [
    path('register/',userregister.as_view(),name='register'),
    path('login/',LoginView.as_view(),name='login'),
    path('profile/',ProfileView.as_view(),name='profile'),
    path("cart/", CartView.as_view()),
    path("cart/add/", AddToCartView.as_view()),
    path("product/",ProductView.as_view()),
    path("addproduct/",AddProductView.as_view()),
    path("addproduct/<int:pk>/",AddProductView.as_view()),
    path("notification/",NotificationListView.as_view()),
    #razorpay 
    path('', views.index, name="home"),
    path('create-link/', CreatePaymentLink.as_view(), name='create_payment_link'),
    path('webhook/', razorpay_webhook, name='razorpay_webhook'),
    # path('callback/', PaymentCallback.as_view(), name='payment_callback'),
    path('order/',PurchaseView.as_view()),
    path('logout/',LogoutView.as_view()),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # login
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logoutview/', UserLoginStatsView.as_view(), name='logout'),
    path('loginview/',views.loginview,name='loginview'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)