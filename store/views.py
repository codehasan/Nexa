from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    RetrieveModelMixin,
)
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from store.filters import ProductFilter
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
from store.pagination import TenObjectPagination
from store.permissions import IsAdminUserOrReadOnly
from store.serializers import (
    AddCartItemSerializer,
    AddOrderSerializer,
    CartSerializer,
    CollectionSerializer,
    CustomerSerializer,
    GetCartItemSerializer,
    GetOrderSerializer,
    ProductSerializer,
    ReviewSerializer,
    UpdateCartItemSerializer,
    UpdateOrderSerializer,
)


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.select_related("collection").all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter
    pagination_class = TenObjectPagination
    permission_classes = [IsAdminUserOrReadOnly]

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
    permission_classes = [IsAdminUserOrReadOnly]

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
    permission_classes = [AllowAny]


class CartItemViewSet(ModelViewSet):
    http_method_names = ["get", "post", "patch", "delete"]
    permission_classes = [AllowAny]

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


class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminUser]

    def get_serializer_context(self):
        return {"request": self.request}

    @action(
        detail=False,
        methods=["get", "put"],
        permission_classes=[IsAuthenticated],
    )
    def me(self, request):
        customer = Customer.objects.get(user_id=request.user.id)

        if request.method == "GET":
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)

        if request.method == "PUT":
            serializer = CustomerSerializer(
                customer, data=request.data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class OrderViewSet(ModelViewSet):
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def create(self, request, *args, **kwargs):
        serializer = AddOrderSerializer(
            data=request.data, context={"request": self.request}
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = GetOrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        order_id = kwargs["pk"]
        OrderItem.objects.filter(order_id=order_id).delete()
        Order.objects.filter(pk=order_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        if self.request.method in ("PUT", "PATCH", "DELETE"):
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        queryset = Order.objects.prefetch_related("orderitem_set__product")

        if user.is_staff:
            return queryset.all()
        else:
            customer = Customer.objects.only("id").get(user_id=user.id)
            return queryset.filter(customer_id=customer.id)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddOrderSerializer
        elif self.request.method == "PATCH":
            return UpdateOrderSerializer
        return GetOrderSerializer
