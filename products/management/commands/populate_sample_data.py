from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from products.models import Category, Product
from accounts.models import UserProfile
from decimal import Decimal
import random

class Command(BaseCommand):
    help = 'Populate the database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')

        # Create sample users
        users_data = [
            {'username': 'john_doe', 'email': 'john@university.edu', 'first_name': 'John', 'last_name': 'Doe'},
            {'username': 'jane_smith', 'email': 'jane@university.edu', 'first_name': 'Jane', 'last_name': 'Smith'},
            {'username': 'mike_wilson', 'email': 'mike@university.edu', 'first_name': 'Mike', 'last_name': 'Wilson'},
            {'username': 'sarah_jones', 'email': 'sarah@university.edu', 'first_name': 'Sarah', 'last_name': 'Jones'},
            {'username': 'alex_brown', 'email': 'alex@university.edu', 'first_name': 'Alex', 'last_name': 'Brown'},
        ]

        users = []
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                
                # Create user profile
                UserProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'student_id': f'STU{random.randint(100000, 999999)}',
                        'university': 'Sample University',
                        'phone_number': f'+1-555-{random.randint(1000, 9999)}',
                        'address': f'{random.randint(100, 999)} Campus Drive'
                    }
                )
                self.stdout.write(f'Created user: {user.username}')
            users.append(user)

        # Create categories
        categories_data = [
            {'name': 'Textbooks', 'description': 'Academic textbooks and study materials'},
            {'name': 'Electronics', 'description': 'Laptops, phones, and electronic devices'},
            {'name': 'Clothing', 'description': 'Clothes, shoes, and accessories'},
            {'name': 'Furniture', 'description': 'Dorm and apartment furniture'},
            {'name': 'Sports & Outdoors', 'description': 'Sports equipment and outdoor gear'},
            {'name': 'Services', 'description': 'Tutoring, cleaning, and other services'},
            {'name': 'Food & Beverages', 'description': 'Snacks, drinks, and meal plans'},
            {'name': 'Academic Supplies', 'description': 'Notebooks, pens, and study materials'},
        ]

        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            if created:
                self.stdout.write(f'Created category: {category.name}')
            categories.append(category)

        # Create sample products
        products_data = [
            # Textbooks
            {'title': 'Calculus: Early Transcendentals - 8th Edition', 'category': 'Textbooks', 'price': 89.99, 'condition': 'good', 'description': 'Well-maintained calculus textbook. Some highlighting but all pages intact. Perfect for MATH 101.'},
            {'title': 'Introduction to Psychology - 12th Edition', 'category': 'Textbooks', 'price': 65.50, 'condition': 'like_new', 'description': 'Barely used psychology textbook. No writing or highlighting. Includes access code.'},
            {'title': 'Organic Chemistry Study Guide', 'category': 'Textbooks', 'price': 25.00, 'condition': 'fair', 'description': 'Comprehensive study guide for organic chemistry. Some wear but very helpful for exams.'},
            
            # Electronics
            {'title': 'MacBook Air M1 - 13 inch', 'category': 'Electronics', 'price': 899.99, 'condition': 'like_new', 'description': 'Excellent condition MacBook Air. Perfect for students. Includes charger and original box.'},
            {'title': 'iPhone 12 - 128GB', 'category': 'Electronics', 'price': 499.99, 'condition': 'good', 'description': 'Unlocked iPhone 12 in good condition. Minor scratches on back but screen is perfect.'},
            {'title': 'Scientific Calculator TI-84 Plus', 'category': 'Electronics', 'price': 45.00, 'condition': 'good', 'description': 'Reliable calculator for math and science courses. All functions working perfectly.'},
            {'title': 'Wireless Bluetooth Headphones', 'category': 'Electronics', 'price': 79.99, 'condition': 'new', 'description': 'Brand new noise-cancelling headphones. Perfect for studying in the library.'},
            
            # Clothing
            {'title': 'University Hoodie - Size M', 'category': 'Clothing', 'price': 35.00, 'condition': 'good', 'description': 'Official university hoodie in medium. Comfortable and warm for campus walks.'},
            {'title': 'Nike Running Shoes - Size 9', 'category': 'Clothing', 'price': 65.00, 'condition': 'like_new', 'description': 'Barely worn Nike running shoes. Great for gym or casual wear.'},
            {'title': 'Winter Jacket - Size L', 'category': 'Clothing', 'price': 55.00, 'condition': 'good', 'description': 'Warm winter jacket perfect for cold campus weather. Very comfortable.'},
            
            # Furniture
            {'title': 'Study Desk with Drawers', 'category': 'Furniture', 'price': 120.00, 'condition': 'good', 'description': 'Solid wood study desk with multiple drawers. Perfect for dorm room or apartment.'},
            {'title': 'Mini Refrigerator', 'category': 'Furniture', 'price': 85.00, 'condition': 'like_new', 'description': 'Compact fridge perfect for dorm room. Energy efficient and quiet.'},
            {'title': 'Desk Chair - Ergonomic', 'category': 'Furniture', 'price': 75.00, 'condition': 'good', 'description': 'Comfortable office chair with lumbar support. Great for long study sessions.'},
            {'title': 'Bookshelf - 5 Tier', 'category': 'Furniture', 'price': 40.00, 'condition': 'fair', 'description': 'Wooden bookshelf with 5 shelves. Some minor scratches but very functional.'},
            
            # Sports & Outdoors
            {'title': 'Mountain Bike - 21 Speed', 'category': 'Sports & Outdoors', 'price': 299.99, 'condition': 'good', 'description': 'Reliable mountain bike perfect for campus commuting. Recently serviced.'},
            {'title': 'Tennis Racket with Case', 'category': 'Sports & Outdoors', 'price': 45.00, 'condition': 'like_new', 'description': 'Professional tennis racket with protective case. Barely used.'},
            {'title': 'Yoga Mat - Premium', 'category': 'Sports & Outdoors', 'price': 25.00, 'condition': 'new', 'description': 'High-quality yoga mat with carrying strap. Perfect for fitness classes.'},
            
            # Services
            {'title': 'Math Tutoring - Calculus & Algebra', 'category': 'Services', 'price': 30.00, 'condition': 'new', 'description': 'Experienced math tutor offering help with calculus and algebra. $30/hour.'},
            {'title': 'Essay Writing & Editing Service', 'category': 'Services', 'price': 25.00, 'condition': 'new', 'description': 'Professional writing assistance for essays and papers. Quick turnaround.'},
            
            # Academic Supplies
            {'title': 'Scientific Calculator - Casio', 'category': 'Academic Supplies', 'price': 35.00, 'condition': 'like_new', 'description': 'Advanced scientific calculator perfect for engineering courses.'},
            {'title': 'Notebook Set - 5 Pack', 'category': 'Academic Supplies', 'price': 15.00, 'condition': 'new', 'description': 'Set of 5 college-ruled notebooks. Perfect for note-taking.'},
        ]

        locations = [
            'Main Library', 'Student Union', 'Campus Center', 'Dorm Building A', 
            'Engineering Building', 'Science Hall', 'Cafeteria', 'Gym Entrance'
        ]

        for product_data in products_data:
            # Find the category
            category = next((cat for cat in categories if cat.name == product_data['category']), categories[0])
            
            # Random seller
            seller = random.choice(users)
            
            product, created = Product.objects.get_or_create(
                title=product_data['title'],
                defaults={
                    'seller': seller,
                    'description': product_data['description'],
                    'category': category,
                    'price': Decimal(str(product_data['price'])),
                    'condition': product_data['condition'],
                    'status': 'available',
                    'location': random.choice(locations),
                }
            )
            if created:
                self.stdout.write(f'Created product: {product.title}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created sample data:\n'
                f'- {len(users)} users\n'
                f'- {len(categories)} categories\n'
                f'- {Product.objects.count()} products'
            )
        )