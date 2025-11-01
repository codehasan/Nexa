from django.contrib import admin
from django.core.checks import messages
from django.db.models import Count
from django.http.request import HttpRequest
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode

from store.models import (
    Address,
    Cart,
    Collection,
    Customer,
    Order,
    OrderItem,
    Product,
    Promotion,
)


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ["title", "featured", "product_count"]
    list_select_related = ["featured_product"]
    list_per_page = 10
    search_fields = ["title"]

    @admin.display(ordering="featured_product__title")
    def featured(self, collection: Collection):
        return (
            collection.featured_product.title
            if collection.featured_product
            else None
        )

    @admin.display(ordering="product_count")
    def product_count(self, collection: Collection):
        url = (
            reverse("admin:store_product_changelist")
            + "?"
            + urlencode({"collection__id": collection.id})
        )
        return format_html(
            '<a href="{}">{}</a>', url, collection.product_count
        )

    def get_queryset(self, request: HttpRequest):
        return (
            super()
            .get_queryset(request)
            .annotate(product_count=Count("product"))
        )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["title", "price", "inventory", "collection_name"]
    list_select_related = ["collection"]
    list_editable = ["price", "inventory"]
    list_filter = ["collection__title", "last_update"]
    list_per_page = 10
    search_fields = ["title", "collection__title"]
    prepopulated_fields = {
        "slug": ["title"],
    }
    autocomplete_fields = ["collection", "promotions"]
    actions = ["clear_inventory"]

    @admin.display(ordering="collection__title")
    def collection_name(self, product: Product):
        return product.collection.title if product.collection else None

    @admin.action(description="Clear inventory")
    def clear_inventory(self, request, queryset):
        update_count = queryset.update(inventory=0)
        if update_count > 0:
            self.message_user(
                request,
                f"Updated {update_count} products inventory",
                messages.SUCCESS,
            )
        else:
            self.message_user(
                request,
                "No products were updated",
                messages.ERROR,
            )


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ["description", "discount"]
    list_per_page = 10
    search_fields = ["description"]


class CustomerFilter(admin.SimpleListFilter):
    title = "Orders"
    parameter_name = "order_count"

    def lookups(self, request, model_admin):
        return [
            ("1", "1"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "1":
            return queryset.filter(order_count=1)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = [
        "user__first_name",
        "user__last_name",
        "user__email",
        "membership",
        "orders",
    ]
    list_select_related = ["user"]
    list_editable = ["membership"]
    list_filter = ["membership", CustomerFilter]
    list_per_page = 10
    search_fields = [
        "user__first_name",
        "user__last_name",
        "user__email",
        "user__username",
    ]

    @admin.display(ordering="order_count")
    def orders(self, customer: Customer):
        url = (
            reverse("admin:store_order_changelist")
            + "?"
            + urlencode({"customer__id": customer.id})
        )
        return format_html('<a href="{}">{}</a>', url, customer.order_count)

    def get_queryset(self, request: HttpRequest):
        return (
            super().get_queryset(request).annotate(order_count=Count("order"))
        )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ["street", "city", "zip"]
    list_per_page = 10
    search_fields = ["street", "city", "zip"]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    autocomplete_fields = ["product"]
    min_num = 0
    max_num = 10
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["placed_at", "payment_status", "customer_name"]
    list_select_related = ["customer"]
    list_editable = ["payment_status"]
    list_filter = ["payment_status", "placed_at"]
    list_per_page = 10
    autocomplete_fields = ["customer"]
    search_fields = ["customer__first_name", "customer__last_name"]
    inlines = [OrderItemInline]

    def customer_name(self, order: Order):
        return f"{order.customer.first_name} {order.customer.last_name}"


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ["create_at"]
    list_per_page = 10
