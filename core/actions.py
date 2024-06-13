import csv
import json
from datetime import datetime
from decimal import ROUND_HALF_UP
from decimal import Decimal
from io import StringIO
from typing import Any
from typing import BinaryIO

import httpx
from django.contrib import admin
from django.contrib import messages
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.http.response import HttpResponseRedirect
from django.utils import timezone
from form_action import extra_button  # type: ignore

from core import exceptions
from core import models
from core.forms import OrderUploadForm


class DecimalEncoder(json.JSONEncoder):
    def default(self, o: Any):
        if isinstance(o, Decimal):
            return str(o)
        return super().default(o)


def get_unique_values(data: list[Any], unique_field: str = "id") -> list[Any]:
    try:
        return list(d[unique_field] for d in data)
    except KeyError:
        return []


def data_cleanup(raw: dict[str, Any]):
    # shallow copy
    data = dict(raw)
    # trim leading and trailing spaces
    for key in data:
        data[key] = data[key].strip()

    # title case
    data["full_name"] = data["full_name"].title()
    data["address"] = data["address"].title()

    # category titles:
    # Men:
    # Turtleneck-Tee, T-Shirt, Trouser, Shorts, Hoodie, DLT, Sweatshirt
    # Longsleeve, Zipper-Hoodie, Sweatpant, Turtleneck-Sweatshirt
    # Pullover-Sweatshirt, Set-Pullover, Pant, Inner-Longsleeve
    # Women:
    # Women-Crop-Longsleeve
    c_title_l = data["c_title"].lower()
    if c_title_l == "tee":
        data["c_title"] = "T-Shirt"
    elif c_title_l == "long-sleeve-tee":
        data["c_title"] = "Longsleeve"
    elif c_title_l == "turtle neck tee":
        data["c_title"] = "Turtleneck-Tee"
    elif c_title_l == "turtle neck sweatshirt":
        data["c_title"] = "Turtleneck-Sweatshirt"
    elif c_title_l == "dlt":
        data["c_title"] = "DLT"
    elif c_title_l == "crop-long-sleeve":
        data["c_title"] = "Women-Crop-Longsleeve"
    else:
        data["c_title"] = data["c_title"].title().replace(" ", "-")

    # size types:
    # S, M, L, XL, XXL, XXXL, Free
    if data["s_name"] == "3XL":
        data["s_name"] = models.SizeChoices.XXXL
    elif data["s_name"] == "2XL":
        data["s_name"] = models.SizeChoices.XXL
    elif data["s_name"] == "Free-Size":
        data["s_name"] = models.SizeChoices.FREE
    elif data["s_name"] == "":
        data["s_name"] = models.SizeChoices.FREE
    if data["s_name"] not in models.SizeChoices.values:
        raise Exception(f"Invalid size type: {data['s_name']}")

    # color types:
    data["c_name"] = data["c_name"].title()
    if data["c_name"] == "":
        data["c_name"] = models.ColorChoices.BLACK
    if data["c_name"] not in models.ColorChoices.values:
        raise Exception(f"Invalid color type: {data['c_name']}")

    # product title
    data["p_title"] = (
        data["p_title"].upper().replace('"', "").replace(" ", "-")
    )

    # order medium
    data["medium"] = data["medium"].title()
    if data["medium"] == "Physically":
        data["medium"] = models.MediumChoices.CONTACT
    elif data["medium"] == "":
        data["medium"] = models.MediumChoices.WEBSITE
    if data["medium"] not in models.MediumChoices.values:
        raise Exception(f"Invalid order medium: {data['medium']}")

    # status
    if data["status"] == "Issue":
        data["status"] = models.StatusChoices.DISPUTED
    elif data["status"] == "Ready-to-Ship":
        data["status"] = models.StatusChoices.PROCESSED
    elif data["status"] in ["New Orders", "INSTOCK"]:
        data["status"] = models.StatusChoices.PENDING
    elif data["status"] == "OH HOLD":
        data["status"] = models.StatusChoices.ONHOLD
    elif data["status"] == "":
        data["status"] = models.StatusChoices.PENDING
    if data["status"] not in models.StatusChoices.values:
        data["status"] = models.StatusChoices.PENDING

    # pricing
    data["subtotal_price"] = (
        Decimal(data["subtotal_price"])
        if data["subtotal_price"]
        else Decimal("0.00")
    )
    data["total_price"] = (
        Decimal(data["total_price"])
        if data["total_price"]
        else Decimal("0.00")
    )
    data["price"] = (
        Decimal(data["price"]) if data["price"] else Decimal("0.00")
    )
    data["discount"] = (
        Decimal(data["discount"]) if data["discount"] else Decimal("0.00")
    )
    data["delivery_charge"] = (
        Decimal(data["delivery_charge"])
        if data["delivery_charge"]
        else Decimal("0.00")
    )

    # paid
    if data["is_paid"] == "Paid":
        data["is_paid"] = True
    else:
        data["is_paid"] = False

    # dates
    try:
        # "ordered_at": "26/05/2024"
        data["ordered_at"] = datetime.strptime(data["ordered_at"], "%d/%m/%Y")
    except ValueError:
        data["ordered_at"] = timezone.now()
    # "shipped_at": "May 21, 2024"
    data["shipped_at"] = (
        datetime.strptime(data["shipped_at"], "%B %d, %Y")
        if data["shipped_at"]
        else None
    )
    # "paid_at": "May 21, 2024"
    data["paid_at"] = (
        datetime.strptime(data["paid_at"], "%B %d, %Y")
        if data["paid_at"]
        else None
    )

    # payment method
    data["payment_method"] = data["payment_method"].title()
    if data["payment_method"] not in models.PaymentMethodChoices.values:
        data["payment_method"] = models.PaymentMethodChoices.COD

    # payment items
    data["is_advance"] = False
    if data["amount"]:
        data["is_advance"] = True
        data["amount"] = Decimal(data["amount"])
    elif data["is_paid"] is True:
        data["amount"] = data["total_price"]
    else:
        data["amount"] = Decimal("0.00")

    # giveaway
    data["is_giveaway"] = bool(data["is_giveaway"])

    # disputes
    data["is_disputed"] = bool(data["is_disputed"])

    # quantity
    data["quantity"] = (
        int(data["quantity"].split()[0]) if data["quantity"] else 1
    )
    if data["quantity"] > 1:
        data["price_per_unit"] = (
            data["price"] / Decimal(data["quantity"])
        ).quantize(Decimal("1.00"), rounding=ROUND_HALF_UP)
    else:
        data["price_per_unit"] = data["price"]

    # phone length validation
    data["phone"] = data["phone"][:15]

    # no name
    if not data["full_name"]:
        data["full_name"] = "N/A"

    # no delivery_method, delivery_to
    if data["delivery_method"] == "By Airport":
        data["delivery_method"] = models.DeliveryMethodChoices.AIRPORT
    if data["delivery_method"] == "NCM B2B":
        data["delivery_method"] = models.DeliveryMethodChoices.NCM
    elif data["delivery_method"] == "pick up":
        data["delivery_method"] = models.DeliveryMethodChoices.SELF
    elif data["delivery_method"] not in models.DeliveryMethodChoices.values:
        data["delivery_method"] = models.DeliveryMethodChoices.SELF
    if not data["delivery_to"]:
        data["delivery_to"] = "N/A"

    # empty data
    if data["phone"] == "":
        raise exceptions.EmptyDataError(f"No Phone. User: {data['full_name']}")
    if data["c_title"] == "":
        raise exceptions.EmptyDataError(
            f"No Category Title. User: {data['phone']}"
        )
    if data["p_title"] == "":
        raise exceptions.EmptyDataError(
            f"No Product Title. User: {data['phone']}"
        )

    return data


def upload_previous_orders(file: BinaryIO):
    content = StringIO(file.read().decode("utf-8"))
    reader = csv.reader(content, delimiter=",")
    # skip the headers
    next(reader, None)
    total_count = 0
    count = 0
    customers: list[dict[str, Any]] = []
    categories: list[dict[str, str]] = []
    sizes: list[dict[str, str]] = []
    colors: list[dict[str, str]] = []
    products: list[dict[str, str]] = []
    orders: list[dict[str, Any]] = []
    payment_items: list[dict[str, Any]] = []
    order_items: list[dict[str, Any]] = []
    for row in reader:
        raw_data = {
            "delivery_package_id": row[1],
            "status": row[3],
            "quantity": row[4],
            "full_name": row[5],
            "c_title": row[6],  # category title
            "p_title": row[7],  # product title
            "s_name": row[8],  # size name
            "c_name": row[9],  # color name
            "is_paid": row[10],
            "is_advance": row[10],
            "is_disputed": row[11],
            "dispute_remarks": row[11],
            "total_price": row[12],
            "ordered_at": row[13],  # order
            "shipped_at": row[14],
            "phone": row[15],
            "payment_method": row[16],
            "address": row[17],
            "delivery_to": row[17],
            "subtotal_price": row[18],  # order
            "price": row[18],  # order_item, payment_item.is_advance
            "price_per_unit": row[18],  # order_item, calculate from quantity
            "delivery_charge": row[19],
            "discount": row[20],
            "medium": row[21],
            "delivery_method": row[22],
            "insta_handle": row[23],
            "phone2": row[24],
            "paid_at": row[25],
            "email": row[26],
            "amount": row[27],  # payment item(is_advance=True)
            "is_giveaway": row[28],
            "giveaway_reason": row[28],
        }
        total_count += 1
        try:
            cleaned_data = data_cleanup(raw_data)
        except exceptions.EmptyDataError as e:
            print(e)
            continue
        customer = {
            "full_name": cleaned_data["full_name"],
            "insta_handle": cleaned_data["insta_handle"],
            "email": cleaned_data["email"],
            "phone": cleaned_data["phone"],
            "phone2": cleaned_data["phone2"],
            "address": cleaned_data["address"],
        }
        category = {
            "title": cleaned_data["c_title"],
        }
        size = {
            "name": cleaned_data["s_name"],
        }
        color = {
            "name": cleaned_data["c_name"],
        }
        product = {
            "title": cleaned_data["p_title"],
            "category__title": cleaned_data["c_title"],
        }
        order = {
            "customer__phone": cleaned_data["phone"],  # UNIQUE phone
            "medium": cleaned_data["medium"],
            "status": cleaned_data["status"],
            "subtotal_price": cleaned_data["subtotal_price"],
            "delivery_charge": cleaned_data["delivery_charge"],
            "discount": cleaned_data["discount"],
            "total_price": cleaned_data["total_price"],
            "is_paid": cleaned_data["is_paid"],
            "delivery_to": cleaned_data["delivery_to"],
            "delivery_method": cleaned_data["delivery_method"],
            "delivery_package_id": cleaned_data["delivery_package_id"],
            "ordered_at": cleaned_data["ordered_at"],
            "shipped_at": cleaned_data["shipped_at"],
            "paid_at": cleaned_data["paid_at"],
        }
        payment_item = {
            # order__id
            "payment_method": cleaned_data["payment_method"],
            "amount": cleaned_data["amount"],
            "is_advance": cleaned_data["is_advance"],
        }
        order_item = {
            "product__title": cleaned_data["p_title"],
            # order__id
            "is_giveaway": cleaned_data["is_giveaway"],
            "giveaway_reason": cleaned_data["giveaway_reason"],
            "size": cleaned_data["s_name"],
            "color": cleaned_data["c_name"],
            "quantity": cleaned_data["quantity"],
            "price_per_unit": cleaned_data["price_per_unit"],
            "price": cleaned_data["price"],
            "is_disputed": cleaned_data["is_disputed"],
            "dispute_remarks": cleaned_data["dispute_remarks"],
        }
        customers.append(customer)
        categories.append(category)
        sizes.append(size)
        colors.append(color)
        products.append(product)
        orders.append(order)
        payment_items.append(payment_item)
        order_items.append(order_item)
        count += 1

    # get uniques
    u_customers = get_unique_values(customers, "phone")
    u_categories = get_unique_values(categories, "title")
    u_products = get_unique_values(products, "title")

    # bulk create
    # customers
    models.Customer.objects.bulk_create(
        [models.Customer(**c) for c in customers], ignore_conflicts=True
    )
    customer_ids = {
        c["phone"]: c["id"]
        for c in models.Customer.objects.filter(phone__in=u_customers)
        .values("id", "phone")
        .iterator()
    }
    # categories
    models.Category.objects.bulk_create(
        [models.Category(**c) for c in categories], ignore_conflicts=True
    )
    # get ids for unique category entries
    category_ids = {
        c["title"]: c["id"]
        for c in models.Category.objects.filter(title__in=u_categories)
        .values("id", "title")
        .iterator()
    }
    # sizes
    models.Size.objects.bulk_create(
        [models.Size(**s) for s in sizes], ignore_conflicts=True
    )
    # colors
    models.Color.objects.bulk_create(
        [models.Color(**c) for c in colors], ignore_conflicts=True
    )
    # products
    for p in products:
        p["category_id"] = category_ids[p["category__title"]]
        p.pop("category__title", None)
    models.Product.objects.bulk_create(
        [models.Product(**p) for p in products], ignore_conflicts=True
    )
    product_ids = {
        p["title"]: p["id"]
        for p in models.Product.objects.filter(title__in=u_products)
        .values("id", "title")
        .iterator()
    }
    # orders
    if not (len(orders) == len(payment_items) == len(order_items)):
        raise ValueError(
            "Orders, payment items and order items not equal in len"
        )
    for o in orders:
        o["customer_id"] = customer_ids[o["customer__phone"]]
        o.pop("customer__phone", None)
    order_ids = models.Order.objects.bulk_create(
        [models.Order(**o) for o in orders]
    )
    # payment_items
    for idx, p in enumerate(payment_items):
        p["order_id"] = order_ids[idx].id  # type: ignore
    models.PaymentItem.objects.bulk_create(
        [models.PaymentItem(**p) for p in payment_items]
    )
    # order_items
    for idx, o in enumerate(order_items):
        o["order_id"] = order_ids[idx].id  # type: ignore
        o["product_id"] = product_ids[o["product__title"]]
        o.pop("product__title", None)
    models.OrderItem.objects.bulk_create(
        [models.OrderItem(**o) for o in order_items]
    )

    # remove this codeblock
    with open("test-clean.json", "w") as f:
        json.dump(
            {
                "customers": customers,
                "categories": categories,
                "sizes": sizes,
                "colors": colors,
                "products": products,
                "orders": orders,
                "payment_items": payment_items,
                "order_items": order_items,
            },
            f,
            default=str,
        )

    return count, total_count


@extra_button("Upload Orders (CSV)", OrderUploadForm)
def upload_orders_csv(request: HttpRequest, form: OrderUploadForm):
    try:
        count, total_count = upload_previous_orders(form.cleaned_data["file"])
        if count > 0:
            messages.add_message(
                request,
                messages.INFO,
                f"Successfully uploaded {count} / {total_count} order(s)",
            )
        else:
            messages.add_message(
                request, messages.ERROR, "No orders to upload"
            )
    except Exception as e:
        messages.add_message(
            request, messages.ERROR, "Failed to upload orders"
        )
        raise e

    return HttpResponseRedirect("/admin/core/order/")


@admin.action(description="Create ncm order for selected orders")
def create_ncm_order(
    modeladmin: admin.ModelAdmin,  # type: ignore
    request: HttpRequest,
    queryset: QuerySet[models.Order],
):
    for o in queryset:
        if not o.delivery_ncm_from:
            modeladmin.message_user(
                request,
                f"Order #{o.pk} has no NCM from branch.",
                messages.ERROR,
            )
            return
        if not o.delivery_ncm_to:
            modeladmin.message_user(
                request,
                f"Order #{o.pk} has no NCM delivery branch.",
                messages.ERROR,
            )
            return
    count = 0
    settings, _ = models.Settings.objects.get_or_create(id=1)
    for o in queryset:
        try:
            data = {
                "name": o.customer.full_name,
                "phone": o.customer.phone,
                "phone2": o.customer.phone2,
                "cod_charge": o.total_price if o.is_paid else Decimal("0.00"),
                "address": o.delivery_address,
                "fbranch": o.delivery_ncm_from,
                "branch": o.delivery_ncm_to,
            }
            headers = {"Authorization": f"Token {settings.ncm_key}"}
            res = httpx.post(
                settings.ncm_url + "/api/v1/order/create",
                data=data,
                headers=headers,
            )
            res.raise_for_status()
            order_id = res.json()["orderid"]
            o.ncm_order_id = order_id
            o.save()
            count += 1
        except httpx.HTTPError as e:
            modeladmin.message_user(request, str(e), messages.ERROR)
            return
    modeladmin.message_user(
        request,
        f"Sucessfully created {len(queryset)} NCM orders.",
        messages.SUCCESS,
    )
