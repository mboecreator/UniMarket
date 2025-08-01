from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from .models import Product, Category, Cart, CartItem, Message, ProductLike, ProductView

def home(request):
    """Home page showing featured products"""
    featured_products = Product.objects.filter(status='available')[:6]
    categories = Category.objects.all()
    return render(request, 'products/home.html', {
        'featured_products': featured_products,
        'categories': categories
    })

def products(request):
    """Product listing page with search and filter"""
    products = Product.objects.filter(status='available').select_related('category', 'seller')
    categories = Category.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Category filter
    category_id = request.GET.get('category')
    if category_id:
        try:
            products = products.filter(category_id=int(category_id))
        except (ValueError, TypeError):
            pass
    
    # Price filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except (ValueError, TypeError):
            pass
    
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except (ValueError, TypeError):
            pass
    
    # Sorting
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'popular':
        # For now, order by creation date as we don't have view counts
        products = products.order_by('-created_at')
    else:  # newest
        products = products.order_by('-created_at')
    
    return render(request, 'products/products.html', {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_id
    })

def product_detail(request, product_id):
    """Product detail page"""
    product = get_object_or_404(Product, id=product_id)
    
    # Track product view
    if request.user.is_authenticated:
        ProductView.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'ip_address': get_client_ip(request)}
        )
    else:
        # Track anonymous views by IP
        ProductView.objects.get_or_create(
            product=product,
            ip_address=get_client_ip(request),
            defaults={'user': None}
        )
    
    # Check if user has liked this product
    user_liked = False
    if request.user.is_authenticated:
        user_liked = ProductLike.objects.filter(user=request.user, product=product).exists()
    
    # Get related products from same category
    related_products = Product.objects.filter(
        category=product.category,
        status='available'
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'user_liked': user_liked,
        'related_products': related_products,
    }
    
    return render(request, 'products/product_detail.html', context)

def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@login_required
def cart(request):
    """Shopping cart page"""
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'products/cart.html', {'cart': cart})

@login_required
def add_to_cart(request, product_id):
    """Add product to cart"""
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    messages.success(request, f'{product.title} added to cart!')
    return redirect('product_detail', product_id=product_id)

@login_required
def contact_seller(request, product_id):
    """Allow buyers to contact sellers about products"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        message_type = request.POST.get('message_type', 'inquiry')
        subject = request.POST.get('subject', '')
        content = request.POST.get('content', '')
        offered_price = request.POST.get('offered_price')
        
        if not subject or not content:
            messages.error(request, 'Please fill in all required fields.')
            return redirect('product_detail', product_id=product_id)
        
        # Create message
        message = Message.objects.create(
            sender=request.user,
            recipient=product.seller,
            product=product,
            message_type=message_type,
            subject=subject,
            content=content,
            offered_price=offered_price if offered_price else None
        )
        
        messages.success(request, 'Your message has been sent to the seller!')
        return redirect('product_detail', product_id=product_id)
    
    return redirect('product_detail', product_id=product_id)

@login_required
def toggle_like(request, product_id):
    """Toggle like status for a product"""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        
        like, created = ProductLike.objects.get_or_create(
            user=request.user,
            product=product
        )
        
        if not created:
            like.delete()
            liked = False
        else:
            liked = True
        
        # Get updated like count
        like_count = product.likes.count()
        
        return JsonResponse({
            'liked': liked,
            'like_count': like_count
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
