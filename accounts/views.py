from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Count, Q
from .models import UserProfile, SellerSubscription
from .forms import SimpleUserCreationForm
from products.models import Product, Message, ProductLike, ProductView, Order

def register(request):
    if request.method == 'POST':
        form = SimpleUserCreationForm(request.POST)
        user_type = request.POST.get('user_type', 'buyer')
        
        if form.is_valid():
            user = form.save()
            
            # Create user profile
            UserProfile.objects.create(
                user=user,
                student_id=None,  # Will be filled later in profile completion
                university='',  # Will be filled later in profile completion
            )
            
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created successfully for {username}!')
            
            # Auto-login the user
            login(request, user)
            
            # Redirect based on user type
            if user_type == 'seller':
                return redirect('subscription_plans')
            else:
                return redirect('products')  # Redirect buyers to products page
    else:
        form = SimpleUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        user_type = request.POST.get('user_type', 'buyer')
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                
                # Redirect based on user type
                if user_type == 'seller':
                    # Check if user has seller subscription
                    profile, created = UserProfile.objects.get_or_create(user=user)
                    if profile.can_post_products():
                        return redirect('seller_dashboard')
                    else:
                        return redirect('subscription_plans')
                else:
                    return redirect('products')  # Redirect buyers to products page
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def profile(request):
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    return render(request, 'accounts/profile.html', {'profile': profile})

@login_required
def seller_dashboard(request):
    """Main seller dashboard view"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Check if user has active subscription
    if not profile.can_post_products():
        return redirect('subscription_plans')
    
    # Get seller statistics
    products = Product.objects.filter(seller=request.user)
    total_products = products.count()
    active_products = products.filter(status='available').count()
    sold_products = products.filter(status='sold').count()
    
    # Get recent messages
    recent_messages = Message.objects.filter(
        recipient=request.user
    ).select_related('sender', 'product')[:5]
    
    unread_messages_count = Message.objects.filter(
        recipient=request.user,
        is_read=False
    ).count()
    
    # Get recent product views and likes
    recent_views = ProductView.objects.filter(
        product__seller=request.user
    ).select_related('product', 'user')[:10]
    
    recent_likes = ProductLike.objects.filter(
        product__seller=request.user
    ).select_related('product', 'user')[:10]
    
    context = {
        'profile': profile,
        'total_products': total_products,
        'active_products': active_products,
        'sold_products': sold_products,
        'recent_messages': recent_messages,
        'unread_messages_count': unread_messages_count,
        'recent_views': recent_views,
        'recent_likes': recent_likes,
    }
    
    return render(request, 'accounts/seller_dashboard.html', context)

@login_required
def subscription_plans(request):
    """Display subscription plans for sellers"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Get user's current subscription if any
    current_subscription = SellerSubscription.objects.filter(
        user=request.user,
        payment_status='completed'
    ).order_by('-created_at').first()
    
    context = {
        'profile': profile,
        'current_subscription': current_subscription,
    }
    
    return render(request, 'accounts/subscription_plans.html', context)

@login_required
def subscribe(request):
    """Handle subscription purchase"""
    if request.method == 'POST':
        subscription_type = request.POST.get('subscription_type')
        
        if subscription_type not in ['monthly', 'quarterly', 'yearly']:
            messages.error(request, 'Invalid subscription type.')
            return redirect('subscription_plans')
        
        # Create subscription record
        subscription = SellerSubscription.objects.create(
            user=request.user,
            subscription_type=subscription_type,
            start_date=timezone.now(),
            payment_status='completed'  # In real app, this would be 'pending' until payment is processed
        )
        
        messages.success(request, f'Successfully subscribed to {subscription_type} plan! You can now post products.')
        return redirect('seller_dashboard')
    
    return redirect('subscription_plans')

@login_required
def seller_messages(request):
    """View all messages for seller"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if not profile.can_post_products():
        return redirect('subscription_plans')
    
    messages_list = Message.objects.filter(
        recipient=request.user
    ).select_related('sender', 'product').order_by('-created_at')
    
    context = {
        'messages': messages_list,
    }
    
    return render(request, 'accounts/seller_messages.html', context)

@login_required
def seller_products(request):
    """View and manage seller's products"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if not profile.can_post_products():
        return redirect('subscription_plans')
    
    products = Product.objects.filter(seller=request.user).annotate(
        likes_count=Count('likes'),
        views_count=Count('views'),
        messages_count=Count('messages')
    ).order_by('-created_at')
    
    context = {
        'products': products,
    }
    
    return render(request, 'accounts/seller_products.html', context)

@login_required
def my_orders(request):
    """View user's orders"""
    orders = Order.objects.filter(buyer=request.user).prefetch_related('items__product').order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    
    return render(request, 'accounts/my_orders.html', context)
