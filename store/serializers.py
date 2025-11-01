from django.utils.text import slugify
import uuid
from rest_framework import serializers
from store.models import Cart, CartItem, Collection, Product, Review


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
