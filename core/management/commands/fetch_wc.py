from typing import Any

import httpx
from django.core.management import CommandError
from django.core.management.base import BaseCommand
from django.db import transaction

from core import models
from core.models import Settings
from core.models import StatusChoices
from core.serializers import WcNewOrderSerializer


class Command(BaseCommand):
    help = "Fetch orders from woocommerce"

    def handle(self, *args: Any, **options: Any):
        print("Fetching orders from woocommerce...")
        settings, _ = Settings.objects.get_or_create(id=1)
        if not settings.wc_url:
            raise CommandError("wc_url not set.")
        if not settings.wc_consumer_key:
            raise CommandError("wc_consumer_key not set.")
        if not settings.wc_consumer_secret:
            raise CommandError("wc_consumer_secret not set.")
        res = httpx.get(
            f"{settings.wc_url}/wp-json/wc/v3/orders",
            auth=(settings.wc_consumer_key, settings.wc_consumer_secret),
        )
        res.raise_for_status()
        settings, _ = Settings.objects.get_or_create(id=1)
        for order_data in res.json():
            serializer = WcNewOrderSerializer(data=order_data)
            serializer.is_valid(raise_exception=True)
            wc_data: Any = serializer.validated_data  # type: ignore

            if wc_data["status"] == StatusChoices.CANCELED:
                continue

            # check if order already exists
            if models.Order.objects.filter(
                medium=models.MediumChoices.WEBSITE,
                wc_order_id=wc_data["id"],
            ).exists():
                print("Order already exists.")
                continue

            with transaction.atomic():
                # get or create customer
                customer, created = models.Customer.objects.get_or_create(
                    phone=wc_data["billing"]["phone"],
                )
                if created:
                    customer.full_name = wc_data["billing"]["full_name"]
                    customer.email = wc_data["billing"]["email"]
                    customer.address = wc_data["billing"]["address"]
                    if "phone2" in wc_data["shipping"]:
                        customer.phone2 = wc_data["shipping"]["phone2"]
                    customer.save()

                # get or create category
                category, _ = models.Category.objects.get_or_create(
                    title="UNKNOWN"
                )

                # create order
                order = models.Order.objects.create(
                    customer=customer,
                    medium=models.MediumChoices.WEBSITE,
                    wc_order_id=wc_data["id"],
                    wc_order_key=wc_data["order_key"],
                    status=wc_data["status"],
                    subtotal_price=wc_data["total"]
                    - wc_data["discount_total"]
                    - wc_data["shipping_total"],
                    delivery_charge=wc_data["shipping_total"],
                    discount=wc_data["discount_total"],
                    total_price=wc_data["total"],
                    customer_note=wc_data["customer_note"],
                    delivery_ncm_from=settings.delivery_ncm_from,
                    delivery_ncm_to=wc_data["shipping"]["delivery_ncm_to"],
                    delivery_address=wc_data["shipping"]["address"],
                    delivery_note=wc_data["customer_note"],
                    ordered_at=wc_data["date_created"],
                )

                # get or create product & order_item, for each line_item
                # TODO bulk create
                for item in wc_data["line_items"]:
                    # product
                    product = models.Product.objects.filter(
                        title=item["name"]
                    ).first()
                    if product is None:
                        product = models.Product(
                            title=item["name"], category=category
                        )
                    product.price = item["price_per_unit"]
                    product.wc_product_id = item["product_id"]
                    product.save()

                    # order item
                    order_item = models.OrderItem(
                        product=product,
                        order=order,
                        wc_item_id=item["id"],
                        quantity=item["quantity"],
                        price_per_unit=item["price_per_unit"],
                        discount=item["discount"],
                        price=item["price"],
                    )
                    if item.get("size"):
                        order_item.size = item["size"]
                    if item.get("color"):
                        order_item.color = item["color"]
                    if item.get("include_longsleeve"):
                        order_item.include_longsleeve = item[
                            "include_longsleeve"
                        ]
                    if item.get("logo_variation"):
                        order_item.logo_variation = item["logo_variation"]
                    order_item.save()
        print("Success.")
