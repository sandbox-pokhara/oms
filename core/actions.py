import csv
from form_action import extra_button
from core.forms import OrderUploadForm
from django.contrib import messages
from django.http.response import HttpResponseRedirect
from io import StringIO
import json
from decimal import Decimal, ROUND_HALF_UP

from core import models
from datetime import datetime


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return str(o)
        return super().default(o)


def data_cleanup(raw):
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
    if data["s_name"] not in models.SizeChoices.values:
        raise Exception(f"Invalid size type: {data['s_name']}")

    # color types:
    data["c_name"] = data["c_name"].title()
    if data["c_name"] not in models.ColorChoices.values:
        raise Exception(f"Invalid color type: {data['c_name']}")

    # product title
    data["p_title"] = data["p_title"].upper().replace(
        '"', "").replace(" ", "-")

    # order medium
    data["medium"] = data["medium"].title()
    if data["medium"] == "Physically":
        data["medium"] = models.MediumChoices.CONTACT
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
    if data["status"] not in models.StatusChoices.values:
        data["status"] = models.StatusChoices.PENDING

    # pricing
    data["subtotal_price"] = Decimal(
        data["subtotal_price"]) if data["subtotal_price"] else Decimal('0.00')
    data["total_price"] = Decimal(
        data["total_price"]) if data["total_price"] else Decimal('0.00')
    data["price"] = Decimal(
        data["price"]) if data["price"] else Decimal('0.00')
    data["discount"] = Decimal(
        data["discount"]) if data["discount"] else Decimal('0.00')
    data["delivery_charge"] = Decimal(
        data["delivery_charge"]) if data["delivery_charge"] else Decimal('0.00')

    # paid
    if data["is_paid"] == "Paid":
        data["is_paid"] = True
    else:
        data["is_paid"] = False

    # dates
    # "ordered_at": "26/05/2024"
    data["ordered_at"] = datetime.strptime(data["ordered_at"], "%d/%m/%Y")
    # "shipped_at": "May 21, 2024"
    data["shipped_at"] = datetime.strptime(
        data["shipped_at"], "%B %d, %Y") if data["shipped_at"] else None
    # "paid_at": "May 21, 2024"
    data["paid_at"] = datetime.strptime(
        data["paid_at"], "%B %d, %Y") if data["paid_at"] else None

    # payment method
    data["payment_method"] = data["payment_method"].title()
    if data["payment_method"] not in models.PaymentMethodChoices.values:
        data["payment_method"] = models.PaymentMethodChoices.COD

    # payment items
    data["is_advance"] = False
    if data["amount"]:
        data["is_advance"] = True
        data["amount"] = Decimal(data["amount"])
    elif data["is_paid"] == "Paid":
        data["amount"] = data["total_price"]
    else:
        data["amount"] = Decimal('0.00')

    # giveaway
    data["is_giveaway"] = bool(data["is_giveaway"])

    # disputes
    data["is_disputed"] = bool(data["is_disputed"])

    # quantity
    data["quantity"] = int(data["quantity"].split()[0]
                           ) if data["quantity"] else 1
    if data["quantity"] > 1:
        data["price_per_unit"] = (data["price"] / Decimal(data["quantity"])
                                  ).quantize(Decimal('1.00'), rounding=ROUND_HALF_UP)
    else:
        data["price_per_unit"] = data["price"]

    return data


def upload_previous_orders(file):
    content = StringIO(file.read().decode('utf-8'))
    reader = csv.reader(content, delimiter=',')
    # skip the headers
    next(reader, None)
    count = 0
    customers = []
    categories = []
    sizes = []
    colors = []
    products = []
    orders = []
    payment_items = []
    order_items = []
    for row in reader:
        raw_data = {
            "delivery_package_id": row[1],
            "status": row[3],
            "quantity": row[4],
            "full_name": row[5],
            "c_title": row[6],  # category title
            "p_title": row[7],  # product title
            "s_name": row[8],   # size name
            "c_name": row[9],   # color name
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
            "subtotal_price": row[18],   # order
            "price": row[18],   # order_item, payment_item.is_advance
            "price_per_unit": row[18],   # order_item, calculate from quantity
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
        cleaned_data = data_cleanup(raw_data)
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
            "customer__phone": cleaned_data["phone"],   # UNIQUE phone
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
    with open("test-clean.json", "w") as f:
        json.dump({
            "customers": customers,
            "categories": categories,
            "sizes": sizes,
            "colors": colors,
            "products": products,
            "orders": orders,
            "payment_items": payment_items,
            "order_items": order_items
        }, f, default=str)

    return count


@extra_button("Upload Orders (CSV)", OrderUploadForm)
def upload_orders_csv(request, form):
    try:
        count = upload_previous_orders(form.cleaned_data["file"])
        if count > 0:
            messages.add_message(
                request, messages.INFO, f"Successfully uploaded {count} order(s)"
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
