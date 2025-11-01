from uuid import uuid4
from django.core.validators import MinValueValidator
from django.db import models

from nexa import settings


class Promotion(models.Model):
    description = models.CharField(max_length=255)
    discount = models.DecimalField(max_digits=4, decimal_places=2)

    def __str__(self) -> str:
        return f"{self.description} ({self.discount}%)"


class Collection(models.Model):
    title = models.CharField(max_length=255)
    featured_product = models.ForeignKey(
        "Product",
        on_delete=models.SET_NULL,
        related_name="+",
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return self.title


class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(editable=False)
    description = models.TextField()
    price = models.DecimalField(
        max_digits=6, decimal_places=2, validators=[MinValueValidator(1)]
    )
    inventory = models.IntegerField()
    last_update = models.DateTimeField(auto_now=True)
    collection = models.ForeignKey(Collection, on_delete=models.PROTECT)
    promotions = models.ManyToManyField(Promotion, blank=True)

    def __str__(self) -> str:
        return self.title


class Customer(models.Model):
    MEMBERSHIP_BRONZE = "B"
    MEMBERSHIP_SILVER = "S"
    MEMBERSHIP_GOLD = "G"

    MEMBERSHIP_CHOICES = [
        (MEMBERSHIP_BRONZE, "Bronze"),
        (MEMBERSHIP_SILVER, "Silver"),
        (MEMBERSHIP_GOLD, "Gold"),
    ]

    phone = models.CharField(max_length=50)
    birth_date = models.DateField(null=True, blank=True)
    membership = models.CharField(
        max_length=1, choices=MEMBERSHIP_CHOICES, default=MEMBERSHIP_BRONZE
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return (
            f"{self.user.first_name} {self.user.last_name} ({self.user.email})"
        )


class Order(models.Model):
    PAYMENT_PENDING = "P"
    PAYMENT_COMPLETE = "C"
    PAYMENT_FAILED = "F"

    PAYMENT_CHOICES = [
        (PAYMENT_PENDING, "Pending"),
        (PAYMENT_COMPLETE, "Complete"),
        (PAYMENT_FAILED, "Failed"),
    ]

    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=1, choices=PAYMENT_CHOICES, default=PAYMENT_PENDING
    )
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)]
    )
    unit_price = models.DecimalField(
        max_digits=6, decimal_places=2, validators=[MinValueValidator(1)]
    )


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    create_at = models.DateTimeField(auto_now_add=True, editable=False)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "product"], name="unique_cart_product"
            )
        ]


class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    zip = models.CharField(max_length=50)
    customer = models.OneToOneField(
        Customer, on_delete=models.CASCADE, primary_key=True
    )


class Review(models.Model):
    description = models.TextField()
    date = models.DateField(auto_now_add=True, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    parent = models.ForeignKey(
        "Review",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )
