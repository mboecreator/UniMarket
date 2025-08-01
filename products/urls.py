from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.products, name='products'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    
    # Buyer-Seller Communication
    path('contact-seller/<int:product_id>/', views.contact_seller, name='contact_seller'),
    path('toggle-like/<int:product_id>/', views.toggle_like, name='toggle_like'),
]