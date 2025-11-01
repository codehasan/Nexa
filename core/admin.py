from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from core.models import User
from store.admin import ProductAdmin
from store.models import Product
from tags.models import TaggedItem


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "username",
                    "usable_password",
                    "password1",
                    "password2",
                ),
            },
        ),
    )


class TagInline(GenericTabularInline):
    model = TaggedItem
    autocomplete_fields = ["tag"]
    min_num = 0
    max_num = 10
    extra = 0


class CustomProductAdmin(ProductAdmin):
    inlines = [TagInline]


admin.site.unregister(Product)
admin.site.register(Product, CustomProductAdmin)
