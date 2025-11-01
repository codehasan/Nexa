from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    RetrieveModelMixin,
)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from store.filters import ProductFilter
from store.models import Cart, CartItem, Collection, OrderItem, Product, Review
from store.pagination import TenObjectPagination
from store.serializers import (
    AddCartItemSerializer,
    GetCartItemSerializer,
    CartSerializer,
    CollectionSerializer,
    ProductSerializer,
    ReviewSerializer,
    UpdateCartItemSerializer,
)


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.select_related("collection").all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter
    pagination_class = TenObjectPagination

    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs["pk"]).count() > 0:
            return Response(
                {
                    "error": "Product cannot be deleted because it is associated with an order item."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(
        product_count=Count("product")
    ).all()
    serializer_class = CollectionSerializer

    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(collection_id=kwargs["pk"]).count() > 0:
            return Response(
                {
                    "error": "Collection cannot be deleted because it is associated with a product."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        product_id = self.kwargs["product_pk"]
        return Review.objects.filter(product_id=product_id)

    def get_serializer_context(self):
        return {"product_id": self.kwargs["product_pk"]}


class CartViewSet(
    CreateModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    queryset = Cart.objects.prefetch_related("cartitem_set__product").all()
    serializer_class = CartSerializer


class CartItemViewSet(ModelViewSet):
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        cart_id = self.kwargs["cart_pk"]
        return CartItem.objects.select_related("product").filter(
            cart_id=cart_id
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddCartItemSerializer
        if self.request.method in ("PATCH"):
            return UpdateCartItemSerializer
        return GetCartItemSerializer

    def get_serializer_context(self):
        return {"cart_id": self.kwargs["cart_pk"]}
