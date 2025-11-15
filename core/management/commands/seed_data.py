import random

import faker_commerce
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from faker import Faker

from core.models import User
from likes.models import LikedItem
from store.models import (
    Address,
    Cart,
    CartItem,
    Collection,
    Customer,
    Order,
    OrderItem,
    Product,
    Promotion,
    Review,
)
from tags.models import Tag, TaggedItem


class Command(BaseCommand):
    help = "Generates random data for the store, tags, and likes apps."

    def handle(self, *args, **options):
        self.stdout.write("Generating mock data...")
        fake = Faker()
        fake.add_provider(faker_commerce.Provider)

        # Clean existing data (optional, but good for fresh runs)
        repr(CartItem.objects.all().delete())
        repr(Cart.objects.all().delete())
        repr(OrderItem.objects.all().delete())
        repr(Order.objects.all().delete())
        repr(Product.objects.all().delete())
        repr(Collection.objects.all().delete())
        repr(Promotion.objects.all().delete())
        repr(Customer.objects.all().delete())
        repr(Address.objects.all().delete())
        repr(Review.objects.all().delete())
        repr(Tag.objects.all().delete())
        repr(TaggedItem.objects.all().delete())
        repr(LikedItem.objects.all().delete())
        repr(User.objects.filter(is_superuser=False).delete())

        # Create Users
        users = []
        for _ in range(50):
            user = User.objects.create_user(
                username=fake.unique.user_name(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.unique.email(),
                # All mock users have the same password
                password="Pass@123",
            )
            users.append(user)

        # Create Promotions
        promotions = []
        for _ in range(5):
            promotion = Promotion.objects.create(
                description=fake.catch_phrase(),
                discount=round(random.uniform(5, 20), 2),
            )
            promotions.append(promotion)

        # Create Collections
        collections = []
        for _ in range(10):
            collection = Collection.objects.create(
                title=fake.ecommerce_category()
            )
            collections.append(collection)

        # Create Products
        products = []
        for _ in range(100):
            product = Product.objects.create(
                title=fake.ecommerce_name(),
                slug=fake.slug(),
                description=fake.paragraph(),
                price=round(random.uniform(10, 9999.99), 2),
                inventory=random.randint(0, 100),
                collection=random.choice(collections),
            )
            # Add promotions to products
            product_promotions = random.sample(
                promotions, random.randint(0, len(promotions))
            )
            product.promotions.set(product_promotions)
            products.append(product)

        # Update featured product for some collections
        for collection in collections:
            if (
                random.random() < 0.5 and products
            ):  # 50% chance to have a featured product
                collection.featured_product = random.choice(products)
                collection.save()

        # Retrieve Customers
        # Customer is created by signal when User is created
        customers = Customer.objects.all()

        # Update Customers and create Addresses
        for customer in customers:
            customer.phone = fake.phone_number()
            customer.birth_date = fake.date_of_birth(
                minimum_age=18, maximum_age=90
            )
            customer.membership = random.choice(
                [
                    Customer.MEMBERSHIP_BRONZE,
                    Customer.MEMBERSHIP_SILVER,
                    Customer.MEMBERSHIP_GOLD,
                ]
            )
            customer.save()

            Address.objects.create(
                street=fake.street_address(),
                city=fake.city(),
                zip=fake.postcode()[:50],
                customer=customer,
            )

        # Create Reviews
        reviews = []
        for _ in range(1000):
            review = Review.objects.create(
                description=fake.paragraph(),
                product=random.choice(products),
                customer=random.choice(customers),
            )
            reviews.append(review)

        # Create Orders
        orders = []
        for _ in range(30):
            order = Order.objects.create(
                customer=random.choice(customers),
                payment_status=random.choice(
                    [
                        Order.PAYMENT_PENDING,
                        Order.PAYMENT_COMPLETE,
                        Order.PAYMENT_FAILED,
                    ]
                ),
            )
            orders.append(order)

        # Create OrderItems
        for order in orders:
            num_items = random.randint(1, 5)
            selected_products = random.sample(products, num_items)
            for product in selected_products:
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=random.randint(1, 10),
                    # Use product's price at the time of order
                    unit_price=product.price,
                )

        # Create Carts and CartItems
        carts = []
        for _ in range(20):
            cart = Cart.objects.create()
            carts.append(cart)

            num_items = random.randint(1, 5)
            selected_products = random.sample(products, num_items)
            for product in selected_products:
                CartItem.objects.create(
                    cart=cart, product=product, quantity=random.randint(1, 5)
                )

        # Create Tags
        tags = []
        for _ in range(15):
            tag = Tag.objects.create(label=fake.unique.word().capitalize())
            tags.append(tag)

        # Create TaggedItems for Products and Collections
        product_content_type = ContentType.objects.get_for_model(Product)
        collection_content_type = ContentType.objects.get_for_model(Collection)

        for product in products:
            if random.random() < 0.7 and tags:  # 70% chance to have tags
                selected_tags = random.sample(
                    tags, random.randint(1, min(3, len(tags)))
                )
                for tag in selected_tags:
                    TaggedItem.objects.create(
                        tag=tag,
                        content_type=product_content_type,
                        object_id=product.id,
                    )

        for collection in collections:
            if random.random() < 0.4 and tags:  # 40% chance to have tags
                selected_tags = random.sample(
                    tags, random.randint(1, min(2, len(tags)))
                )
                for tag in selected_tags:
                    TaggedItem.objects.create(
                        tag=tag,
                        content_type=collection_content_type,
                        object_id=collection.id,
                    )

        # Create LikedItems for Products
        for user in users:
            if (
                random.random() < 0.8 and products
            ):  # 80% chance to like some products
                num_likes = random.randint(1, 5)
                liked_products = random.sample(products, num_likes)
                for product in liked_products:
                    LikedItem.objects.create(
                        user=user,
                        content_type=product_content_type,
                        object_id=product.id,
                    )

        self.stdout.write(
            self.style.SUCCESS("Mock data generated successfully!")
        )
