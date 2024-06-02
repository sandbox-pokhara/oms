from django.contrib import admin
from core import models
from form_action import ExtraButtonMixin
from core.actions import upload_orders_csv


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'insta_handle', 'phone')

    ordering = ('-id',)

    search_fields = ('id', 'full_name', 'insta_handle',
                     'phone', 'email', 'phone2', 'address')

    list_filter = ('gender',)


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')

    ordering = ('-id',)

    search_fields = ('id', 'title')

    list_filter = ('title',)


@admin.register(models.Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

    ordering = ('-id',)

    search_fields = ('id', 'name')

    list_filter = ('name',)


@admin.register(models.Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

    ordering = ('-id',)

    search_fields = ('id', 'name')

    list_filter = ('name',)


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'stock', 'price')

    ordering = ('-id',)

    search_fields = ('id', 'title', 'category__title', 'stock', 'price')

    list_filter = ('category', 'stock', 'price')

    list_editable = ('stock',)

    autocomplete_fields = ('category', 'available_sizes', 'available_colors')


@admin.register(models.Order)
class OrderAdmin(ExtraButtonMixin, admin.ModelAdmin):
    list_display = ('id', 'customer', 'total_price', 'status',
                    'is_paid', 'delivery_to', 'delivery_method')

    ordering = ('-id',)

    search_fields = ('id', 'customer__full_name', 'customer__insta_handle',
                     'customer__phone', 'customer__email', 'customer__phone2', 'customer__address')

    list_filter = ('status', 'customer__gender', 'is_paid', 'delivery_method')

    # extra_buttons = (upload_orders_csv,)


@admin.register(models.PaymentItem)
class PaymentItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'payment_method', 'amount', 'is_advance')

    ordering = ('-id',)

    search_fields = ('id', 'order__id', 'order__customer__full_name', 'order__customer__insta_handle',
                     'order__customer__phone', 'order__customer__email', 'order__customer__phone2', 'order__customer__address')

    list_filter = ('payment_method', 'is_advance')

    list_editable = ('amount', 'is_advance')

    autocomplete_fields = ('order',)


@admin.register(models.OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'price')

    ordering = ('-id',)

    search_fields = ('id', 'order__id', 'order__customer__full_name', 'order__customer__insta_handle',
                     'order__customer__phone', 'order__customer__email', 'order__customer__phone2', 'order__customer__address')

    list_filter = ('order__customer__gender',)

    list_editable = ('quantity', 'price')

    autocomplete_fields = ('order', 'product')
