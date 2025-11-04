import uuid

from django.contrib.auth.models import AnonymousUser
from django.utils.text import slugify
from rest_framework import serializers
from django.db import transaction

from store.models import (
    Cart,
    CartItem,
    Collection,
    Customer,
    Order,
    OrderItem,
    Product,
    Review,
)
from store.signals import order_created


class CollectionSerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Collection
        fields = ["id", "title", "product_count"]


class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "slug",
            "price",
        ]


class ProductSerializer(serializers.ModelSerializer):
    collection = serializers.SerializerMethodField(
        method_name="get_collection"
    )

    def get_collection(self, product: Product) -> dict:
        return {
            "id": product.collection.id,
            "title": product.collection.title,
        }

    def update(self, instance: Product, validated_data: dict) -> Product:
        if "title" in validated_data:
            validated_data["slug"] = (
                slugify(validated_data["title"]) + "-" + str(uuid.uuid4())
            )
        return super().update(instance, validated_data)

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "price",
            "inventory",
            "collection",
        ]


class ReviewSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        product_id = self.context["product_id"]
        return Review.objects.create(product_id=product_id, **validated_data)

    class Meta:
        model = Review
        fields = [
            "id",
            "description",
            "date",
            "customer",
            "parent",
        ]


class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError("No product found with given id")
        return value

    def save(self, **kwargs):
        cart_id = self.context["cart_id"]
        product_id = self.validated_data["product_id"]
        quantity = self.validated_data["quantity"]

        try:
            cart_item = CartItem.objects.get(
                cart_id=cart_id, product_id=product_id
            )
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(
                cart_id=cart_id, **self.validated_data
            )
        return self.instance

    class Meta:
        model = CartItem
        fields = ["id", "quantity", "product_id"]


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["quantity"]


class GetCartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer(read_only=True)
    total_price = serializers.SerializerMethodField(
        method_name="get_total_price"
    )

    def get_total_price(self, cart_item: CartItem) -> float:
        return cart_item.quantity * cart_item.product.price

    class Meta:
        model = CartItem
        fields = ["id", "quantity", "product", "total_price"]


class CartSerializer(serializers.ModelSerializer):
    items = GetCartItemSerializer(
        many=True, read_only=True, source="cartitem_set"
    )
    total_price = serializers.SerializerMethodField(
        method_name="get_total_price"
    )

    def get_total_price(self, cart: Cart) -> float:
        return sum(
            item.quantity * item.product.price
            for item in cart.cartitem_set.all()
        )

    class Meta:
        model = Cart
        fields = ["id", "items", "total_price"]


class CustomerSerializer(serializers.ModelSerializer):
    def validate_membership(self, value):
        user = self.context["request"].user or AnonymousUser()

        if (
            self.instance
            and self.instance.membership != value
            and not user.is_staff
        ):
            raise serializers.ValidationError(
                "You are not allowed to change the membership level."
            )
        return value

    class Meta:
        model = Customer
        fields = ["id", "user_id", "phone", "birth_date", "membership"]


class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "unit_price", "quantity"]


class GetOrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(
        many=True, read_only=True, source="orderitem_set"
    )

    class Meta:
        model = Order
        fields = ["id", "customer_id", "placed_at", "payment_status", "items"]


class AddOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, value):
        if not Cart.objects.filter(pk=value).exists():
            raise serializers.ValidationError("No cart found with given id")

        if CartItem.objects.filter(cart_id=value).count() == 0:
            raise serializers.ValidationError("Cart is empty")

        return value

    @transaction.atomic()
    def save(self, **kwargs):
        user = self.context["request"].user
        customer = Customer.objects.only("id").get(user_id=user.id)
        cart_id = self.validated_data["cart_id"]
        order = Order.objects.create(customer_id=customer.id)
        cart_items = CartItem.objects.select_related("product").filter(
            cart_id=cart_id
        )
        order_items = [
            OrderItem(
                order=order,
                product=item.product,
                quantity=item.quantity,
                unit_price=item.product.price,
            )
            for item in cart_items
        ]
        OrderItem.objects.bulk_create(order_items)
        Cart.objects.filter(pk=cart_id).delete()
        order_created.send_robust(self.__class__, order=order)
        return order


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["payment_status"]
