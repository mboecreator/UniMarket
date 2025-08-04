from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from .models import Product, Category, Cart, CartItem, Message, ProductLike, ProductView, ProductImage, Order, OrderItem
from accounts.models import UserProfile

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
    
    # Get liked products for authenticated users
    liked_products = []
    if request.user.is_authenticated:
        liked_products = list(ProductLike.objects.filter(
            user=request.user,
            product__in=products
        ).values_list('product_id', flat=True))
    
    return render(request, 'products/products.html', {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_id,
        'liked_products': liked_products
    })

def product_detail(request, product_id):
    """Product detail page"""
    product = get_object_or_404(Product, id=product_id)
    
    # Track product view
    try:
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
    except Exception as e:
        # Log error but don't break the page
        print(f"Error tracking product view: {e}")
    
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
    
    # Prevent sellers from contacting themselves
    if request.user == product.seller:
        messages.error(request, 'You cannot contact yourself about your own product.')
        return redirect('product_detail', product_id=product_id)
    
    if request.method == 'POST':
        message_type = request.POST.get('message_type', 'inquiry')
        subject = request.POST.get('subject', '')
        content = request.POST.get('content', '')
        offered_price = request.POST.get('offered_price')
        
        if not subject or not content:
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'products/contact_seller.html', {'product': product})
        
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
    
    # Get existing messages between this buyer and seller for this product
    existing_messages = Message.objects.filter(
        product=product,
        sender__in=[request.user, product.seller],
        recipient__in=[request.user, product.seller]
    ).order_by('created_at')
    
    context = {
        'product': product,
        'existing_messages': existing_messages,
    }
    
    return render(request, 'products/contact_seller.html', context)

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
            'success': True,
            'liked': liked,
            'like_count': like_count
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

@login_required
def add_product(request):
    """Add a new product - only for sellers with active subscription"""
    try:
        user_profile = request.user.userprofile
        if not user_profile.can_post_products():
            messages.error(request, 'You need an active seller subscription to post products.')
            return redirect('subscription_plans')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Please complete your profile first.')
        return redirect('profile')
    
    if request.method == 'POST':
        # Get form data
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        category_id = request.POST.get('category')
        price = request.POST.get('price')
        condition = request.POST.get('condition')
        location = request.POST.get('location', '').strip()
        seller_phone = request.POST.get('seller_phone', '').strip()
        seller_email = request.POST.get('seller_email', '').strip()
        preferred_contact_method = request.POST.get('preferred_contact_method', 'message')
        image = request.FILES.get('image')
        
        # Validation
        errors = []
        if not title:
            errors.append('Title is required.')
        if not description:
            errors.append('Description is required.')
        if not category_id:
            errors.append('Category is required.')
        if not price:
            errors.append('Price is required.')
        if not location:
            errors.append('Meeting location is required.')
        
        try:
            price = float(price)
            if price <= 0:
                errors.append('Price must be greater than 0.')
        except (ValueError, TypeError):
            errors.append('Please enter a valid price.')
        
        try:
            category = Category.objects.get(id=int(category_id))
        except (Category.DoesNotExist, ValueError, TypeError):
            errors.append('Please select a valid category.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'products/add_product.html', {
                'categories': Category.objects.all(),
                'form_data': request.POST
            })
        
        # Create product
        product = Product.objects.create(
            seller=request.user,
            title=title,
            description=description,
            category=category,
            price=price,
            condition=condition,
            location=location,
            seller_phone=seller_phone,
            seller_email=seller_email,
            preferred_contact_method=preferred_contact_method,
            image=image
        )
        
        # Handle additional images
        additional_images = request.FILES.getlist('additional_images')
        for img in additional_images[:5]:  # Limit to 5 additional images
            ProductImage.objects.create(product=product, image=img)
        
        messages.success(request, f'Product "{title}" has been posted successfully!')
        return redirect('product_detail', product_id=product.id)
    
    # GET request - show form
    categories = Category.objects.all()
    
    # Pre-fill contact info from user profile
    user_profile = getattr(request.user, 'userprofile', None)
    initial_data = {
        'seller_phone': user_profile.phone_number if user_profile else '',
        'seller_email': request.user.email,
    }
    
    return render(request, 'products/add_product.html', {
        'categories': categories,
        'initial_data': initial_data
    })

@login_required
def my_products(request):
    """Display seller's products"""
    try:
        user_profile = request.user.userprofile
        if not user_profile.is_seller:
            messages.error(request, 'You need to be a seller to access this page.')
            return redirect('home')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Please complete your profile first.')
        return redirect('profile')
    
    products = Product.objects.filter(seller=request.user).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(products, 12)  # Show 12 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'products/my_products.html', {
        'page_obj': page_obj,
        'products': page_obj
    })

@login_required
def edit_product(request, product_id):
    """Edit an existing product"""
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    
    if request.method == 'POST':
        # Get form data
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        category_id = request.POST.get('category')
        price = request.POST.get('price')
        condition = request.POST.get('condition')
        status = request.POST.get('status')
        location = request.POST.get('location', '').strip()
        seller_phone = request.POST.get('seller_phone', '').strip()
        seller_email = request.POST.get('seller_email', '').strip()
        preferred_contact_method = request.POST.get('preferred_contact_method', 'message')
        image = request.FILES.get('image')
        
        # Validation
        errors = []
        if not title:
            errors.append('Title is required.')
        if not description:
            errors.append('Description is required.')
        if not category_id:
            errors.append('Category is required.')
        if not price:
            errors.append('Price is required.')
        if not location:
            errors.append('Meeting location is required.')
        
        try:
            price = float(price)
            if price <= 0:
                errors.append('Price must be greater than 0.')
        except (ValueError, TypeError):
            errors.append('Please enter a valid price.')
        
        try:
            category = Category.objects.get(id=int(category_id))
        except (Category.DoesNotExist, ValueError, TypeError):
            errors.append('Please select a valid category.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'products/edit_product.html', {
                'product': product,
                'categories': Category.objects.all()
            })
        
        # Update product
        product.title = title
        product.description = description
        product.category = category
        product.price = price
        product.condition = condition
        product.status = status
        product.location = location
        product.seller_phone = seller_phone
        product.seller_email = seller_email
        product.preferred_contact_method = preferred_contact_method
        
        if image:
            product.image = image
        
        product.save()
        
        # Handle additional images
        additional_images = request.FILES.getlist('additional_images')
        for img in additional_images[:5]:  # Limit to 5 additional images
            ProductImage.objects.create(product=product, image=img)
        
        messages.success(request, f'Product "{title}" has been updated successfully!')
        return redirect('product_detail', product_id=product.id)
    
    # GET request - show form
    categories = Category.objects.all()
    
    return render(request, 'products/edit_product.html', {
        'product': product,
        'categories': categories
    })

@login_required
def delete_product(request, product_id):
    """Delete a product"""
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    
    if request.method == 'POST':
        product_title = product.title
        product.delete()
        messages.success(request, f'Product "{product_title}" has been deleted successfully!')
        return redirect('my_products')
    
    return render(request, 'products/delete_product.html', {'product': product})

@login_required
def my_messages(request):
    """View messages for the current user"""
    # Messages received by the user (as seller)
    received_messages = Message.objects.filter(recipient=request.user).order_by('-created_at')
    
    # Messages sent by the user (as buyer)
    sent_messages = Message.objects.filter(sender=request.user).order_by('-created_at')
    
    context = {
        'received_messages': received_messages,
        'sent_messages': sent_messages,
    }
    
    return render(request, 'products/my_messages.html', context)

@login_required
@require_http_methods(["POST"])
def mark_message_read(request, message_id):
    """Mark a message as read"""
    try:
        message = Message.objects.get(id=message_id, recipient=request.user)
        message.is_read = True
        message.save()
        return JsonResponse({'success': True})
    except Message.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Message not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def reply_to_message(request, message_id):
    """Reply to a message"""
    original_message = get_object_or_404(Message, id=message_id, recipient=request.user)
    
    if request.method == 'POST':
        subject = request.POST.get('subject')
        content = request.POST.get('content')
        
        if subject and content:
            # Create reply message
            reply_message = Message.objects.create(
                sender=request.user,
                recipient=original_message.sender,
                product=original_message.product,
                subject=subject,
                content=content,
                message_type=original_message.message_type,
                parent_message=original_message
            )
            
            # Mark original message as replied
            original_message.is_replied = True
            original_message.save()
            
            messages.success(request, 'Reply sent successfully!')
            return redirect('seller_messages')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    context = {
        'original_message': original_message,
    }
    
    return render(request, 'products/reply_message.html', context)

@csrf_exempt
@login_required
def api_add_to_cart(request):
    """API endpoint to add product to cart"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        import json
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        
        if not product_id:
            return JsonResponse({'success': False, 'error': 'Product ID required'}, status=400)
        
        product = get_object_or_404(Product, id=product_id)
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        return JsonResponse({
            'success': True,
            'message': f'{product.title} added to cart!',
            'cart_total': float(cart.get_total_price())
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
def checkout(request):
    """Checkout page"""
    cart = get_object_or_404(Cart, user=request.user)
    
    if not cart.items.exists():
        messages.error(request, 'Your cart is empty.')
        return redirect('cart')
    
    if request.method == 'POST':
        # Process checkout form
        buyer_name = request.POST.get('buyer_name')
        buyer_email = request.POST.get('buyer_email')
        buyer_phone = request.POST.get('buyer_phone')
        delivery_address = request.POST.get('delivery_address')
        delivery_notes = request.POST.get('delivery_notes', '')
        
        # Validate required fields
        if not all([buyer_name, buyer_email, buyer_phone, delivery_address]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'products/checkout.html', {'cart': cart})
        
        try:
            from decimal import Decimal
            # Calculate totals
            subtotal = cart.get_total_price()
            shipping_cost = Decimal('0.00')  # Free campus pickup
            total_amount = subtotal + shipping_cost
            
            # Generate order number
            import random
            import string
            order_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            
            # Create order
            order = Order.objects.create(
                order_number=order_number,
                buyer=request.user,
                buyer_name=buyer_name,
                buyer_email=buyer_email,
                buyer_phone=buyer_phone,
                delivery_address=delivery_address,
                delivery_notes=delivery_notes,
                subtotal=subtotal,
                shipping_cost=shipping_cost,
                total_amount=total_amount,
                status='pending',
                payment_status='pending'
            )
            
            # Create order items
            for cart_item in cart.items.all():
                item_total = Decimal(str(cart_item.quantity)) * cart_item.product.price
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    seller=cart_item.product.seller,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price,
                    total=item_total
                )
            
            # Clear the cart
            cart.items.all().delete()
            
            # Send success message
            messages.success(request, f'Order {order.order_number} has been placed successfully!')
            
            return redirect('checkout_success', order_id=order.id)
            
        except Exception as e:
            messages.error(request, f'An error occurred while processing your order: {str(e)}')
            return render(request, 'products/checkout.html', {'cart': cart})
    
    # GET request - show checkout form
    return render(request, 'products/checkout.html', {'cart': cart})

@login_required
def checkout_success(request, order_id):
    """Checkout success page"""
    order = get_object_or_404(Order, id=order_id, buyer=request.user)
    return render(request, 'products/checkout_success.html', {'order': order})

@csrf_exempt
@login_required
def api_update_cart(request):
    """API endpoint to update cart item quantity"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        import json
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        
        if not product_id:
            return JsonResponse({'success': False, 'error': 'Product ID required'}, status=400)
        
        product = get_object_or_404(Product, id=product_id)
        cart = get_object_or_404(Cart, user=request.user)
        cart_item = get_object_or_404(CartItem, cart=cart, product=product)
        
        if quantity <= 0:
            cart_item.delete()
            message = f'{product.title} removed from cart!'
        else:
            cart_item.quantity = quantity
            cart_item.save()
            message = f'{product.title} quantity updated!'
        
        return JsonResponse({
            'success': True,
            'message': message,
            'total': float(cart.get_total_price())
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
