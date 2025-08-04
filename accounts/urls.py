from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('orders/', views.my_orders, name='my_orders'),
    
    # Seller Dashboard URLs
    path('seller/dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('seller/subscription/', views.subscription_plans, name='subscription_plans'),
    path('seller/subscribe/', views.subscribe, name='subscribe'),
    path('seller/messages/', views.seller_messages, name='seller_messages'),
    path('seller/products/', views.seller_products, name='seller_products'),
]