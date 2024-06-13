from django.contrib import admin
from django.db.models import Sum
from form_action import ExtraButtonMixin

from core import models
from core.actions import upload_orders_csv


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "full_name",
        "phone",
        "get_order_items",
        "get_total_paid",
        "insta_handle",
    )

    ordering = ("-id",)

    search_fields = (
        "id",
        "full_name",
        "insta_handle",
        "phone",
        "email",
        "phone2",
        "address",
    )

    list_filter = ("gender",)

    @admin.display(description="Orderitems")
    def get_order_items(self, obj):
        return models.OrderItem.objects.filter(order__customer=obj).count()

    @admin.display(description="Total paid")
    def get_total_paid(self, obj):
        return models.PaymentItem.objects.filter(
            order__customer=obj
        ).aggregate(Sum("amount"))["amount__sum"]


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "get_products_count")

    ordering = ("-id",)

    search_fields = ("id", "title")

    list_filter = ("title",)

    @admin.display(description="Products")
    def get_products_count(self, obj):
        return models.Product.objects.filter(category=obj).count()


@admin.register(models.Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "get_order_items")

    ordering = ("-id",)

    search_fields = ("id", "name")

    list_filter = ("name",)

    @admin.display(description="Sold count")
    def get_order_items(self, obj):
        return models.OrderItem.objects.filter(size=obj.name).count()


@admin.register(models.Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "get_order_items")

    ordering = ("-id",)

    search_fields = ("id", "name")

    list_filter = ("name",)

    @admin.display(description="Sold count")
    def get_order_items(self, obj):
        return models.OrderItem.objects.filter(color=obj.name).count()


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = (
        "id",
        "title",
        "category",
        "stock",
        "price",
        "get_order_items",
    )

    ordering = ("-id",)

    search_fields = ("id", "title", "category__title", "stock", "price")

    list_filter = ("category", "stock", "price")

    list_editable = ("stock",)

    autocomplete_fields = ("category", "available_sizes", "available_colors")

    @admin.display(description="Sold count")
    def get_order_items(self, obj):
        return obj.order_items.count()


@admin.register(models.Order)
class OrderAdmin(ExtraButtonMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "customer",
        "total_price",
        "status",
        "is_paid",
        "delivery_to",
        "delivery_method",
    )

    ordering = ("-id",)

    search_fields = (
        "id",
        "customer__full_name",
        "customer__insta_handle",
        "customer__phone",
        "customer__email",
        "customer__phone2",
        "customer__address",
    )

    list_filter = ("status", "customer__gender", "is_paid", "delivery_method")

    extra_buttons = (upload_orders_csv,)


@admin.register(models.PaymentItem)
class PaymentItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "payment_method", "amount", "is_advance")

    ordering = ("-id",)

    search_fields = (
        "id",
        "order__id",
        "order__customer__full_name",
        "order__customer__insta_handle",
        "order__customer__phone",
        "order__customer__email",
        "order__customer__phone2",
        "order__customer__address",
    )

    list_filter = ("payment_method", "is_advance")

    autocomplete_fields = ("order",)


@admin.register(models.OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "get_ordered_by",
        "product",
        "quantity",
        "price",
    )

    ordering = ("-id",)

    search_fields = (
        "id",
        "order__id",
        "order__customer__full_name",
        "order__customer__insta_handle",
        "order__customer__phone",
        "order__customer__email",
        "order__customer__phone2",
        "order__customer__address",
    )

    list_filter = ("order__customer__gender",)

    autocomplete_fields = ("order", "product")

    @admin.display(description="Ordered by")
    def get_ordered_by(self, obj):
        return obj.order.customer.full_name


@admin.register(models.Settings)
class SettingsAdmin(admin.ModelAdmin):
    list_display = ("id", "wc_consumer_key", "wc_consumer_secret")
