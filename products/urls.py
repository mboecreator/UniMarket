from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.products, name='products'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    
    # API endpoints for cart
    path('api/cart/add/', views.api_add_to_cart, name='api_add_to_cart'),
    path('api/cart/update/', views.api_update_cart, name='api_update_cart'),
    
    # Checkout
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/success/<int:order_id>/', views.checkout_success, name='checkout_success'),
    
    # Seller Product Management
    path('add-product/', views.add_product, name='add_product'),
    path('my-products/', views.my_products, name='my_products'),
    path('edit-product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete-product/<int:product_id>/', views.delete_product, name='delete_product'),
    
    # Buyer-Seller Communication
    path('contact-seller/<int:product_id>/', views.contact_seller, name='contact_seller'),
    path('my-messages/', views.my_messages, name='my_messages'),
    path('messages/mark-read/<int:message_id>/', views.mark_message_read, name='mark_message_read'),
    path('messages/reply/<int:message_id>/', views.reply_to_message, name='reply_to_message'),
    path('toggle-like/<int:product_id>/', views.toggle_like, name='toggle_like'),
]