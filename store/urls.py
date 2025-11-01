from django.urls import include, path
from rest_framework.routers import SimpleRouter
from rest_framework_nested.routers import NestedSimpleRouter

from store import views

router = SimpleRouter()
router.register(r"products", views.ProductViewSet, basename="product")
router.register(r"collections", views.CollectionViewSet, basename="collection")
router.register(r"carts", views.CartViewSet, basename="cart")

product_router = NestedSimpleRouter(router, r"products", lookup="product")
product_router.register(
    r"reviews", views.ReviewViewSet, basename="product-review"
)

cart_router = NestedSimpleRouter(router, r"carts", lookup="cart")
cart_router.register(r"items", views.CartItemViewSet, basename="cart-item")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(product_router.urls)),
    path("", include(cart_router.urls)),
]
