from decimal import ROUND_HALF_UP
from decimal import Decimal
from typing import Any

from rest_framework import serializers  # type: ignore

from core.models import ColorChoices
from core.models import LogoVariationChoices
from core.models import NCMBranchChoices
from core.models import PaymentMethodChoices
from core.models import SizeChoices
from core.models import StatusChoices

WC_NCM_MAP = {
    "NP001": NCMBranchChoices.POKHARA,
    "NP002": NCMBranchChoices.POKHARA,
    "NP003": NCMBranchChoices.POKHARA,
    "NP004": NCMBranchChoices.POKHARA,
    "NP005": NCMBranchChoices.POKHARA,
    "NP006": NCMBranchChoices.POKHARA,
    "NP007": NCMBranchChoices.POKHARA,
    "NP008": NCMBranchChoices.POKHARA,
    "NP009": NCMBranchChoices.POKHARA,
    "NP010": NCMBranchChoices.POKHARA,
    "NP011": NCMBranchChoices.POKHARA,
    "NP012": NCMBranchChoices.POKHARA,
    "NP013": NCMBranchChoices.POKHARA,
    "NP014": NCMBranchChoices.POKHARA,
    "NP015": NCMBranchChoices.POKHARA,
    "NP016": NCMBranchChoices.POKHARA,
    "NP017": NCMBranchChoices.POKHARA,
    "NP018": NCMBranchChoices.POKHARA,
    "NP019": NCMBranchChoices.POKHARA,
    "NP020": NCMBranchChoices.POKHARA,
    "NP021": NCMBranchChoices.POKHARA,
    "NP022": NCMBranchChoices.POKHARA,
    "NP023": NCMBranchChoices.POKHARA,
    "NP024": NCMBranchChoices.POKHARA,
    "NP025": NCMBranchChoices.POKHARA,
    "NP026": NCMBranchChoices.POKHARA,
    "NP027": NCMBranchChoices.POKHARA,
    "NP028": NCMBranchChoices.POKHARA,
    "NP029": NCMBranchChoices.POKHARA,
    "NP030": NCMBranchChoices.POKHARA,
    "NP031": NCMBranchChoices.POKHARA,
    "NP032": NCMBranchChoices.POKHARA,
    "NP033": NCMBranchChoices.POKHARA,
    "NP034": NCMBranchChoices.POKHARA,
    "NP035": NCMBranchChoices.POKHARA,
    "NP036": NCMBranchChoices.POKHARA,
    "NP037": NCMBranchChoices.POKHARA,
    "NP038": NCMBranchChoices.POKHARA,
    "NP039": NCMBranchChoices.POKHARA,
    "NP040": NCMBranchChoices.POKHARA,
    "NP041": NCMBranchChoices.POKHARA,
    "NP042": NCMBranchChoices.POKHARA,
    "NP043": NCMBranchChoices.POKHARA,
    "NP044": NCMBranchChoices.POKHARA,
    "NP045": NCMBranchChoices.POKHARA,
    "NP046": NCMBranchChoices.POKHARA,
    "NP047": NCMBranchChoices.POKHARA,
    "NP048": NCMBranchChoices.POKHARA,
    "NP049": NCMBranchChoices.POKHARA,
    "NP050": NCMBranchChoices.POKHARA,
    "NP051": NCMBranchChoices.POKHARA,
    "NP052": NCMBranchChoices.POKHARA,
    "NP053": NCMBranchChoices.POKHARA,
    "NP054": NCMBranchChoices.POKHARA,
    "NP055": NCMBranchChoices.POKHARA,
    "NP056": NCMBranchChoices.POKHARA,
    "NP057": NCMBranchChoices.POKHARA,
    "NP058": NCMBranchChoices.POKHARA,
    "NP059": NCMBranchChoices.POKHARA,
    "NP060": NCMBranchChoices.POKHARA,
    "NP061": NCMBranchChoices.POKHARA,
    "NP062": NCMBranchChoices.POKHARA,
    "NP063": NCMBranchChoices.POKHARA,
    "NP064": NCMBranchChoices.POKHARA,
    "NP065": NCMBranchChoices.POKHARA,
    "NP066": NCMBranchChoices.POKHARA,
    "NP067": NCMBranchChoices.POKHARA,
    "NP068": NCMBranchChoices.POKHARA,
    "NP069": NCMBranchChoices.POKHARA,
    "NP070": NCMBranchChoices.POKHARA,
    "NP071": NCMBranchChoices.POKHARA,
    "NP072": NCMBranchChoices.POKHARA,
    "NP073": NCMBranchChoices.POKHARA,
    "NP074": NCMBranchChoices.POKHARA,
    "NP075": NCMBranchChoices.POKHARA,
    "NP076": NCMBranchChoices.POKHARA,
    "NP077": NCMBranchChoices.POKHARA,
    "NP078": NCMBranchChoices.POKHARA,
    "NP079": NCMBranchChoices.POKHARA,
    "NP080": NCMBranchChoices.POKHARA,
    "NP081": NCMBranchChoices.POKHARA,
}


class WcNewOrderSerializer(serializers.Serializer[Any]):
    """Woocommerce webhook serializer for creating order"""

    id = serializers.IntegerField()
    status = serializers.CharField()
    date_created = serializers.DateTimeField()
    discount_total = serializers.DecimalField(max_digits=10, decimal_places=2)
    shipping_total = serializers.DecimalField(max_digits=10, decimal_places=2)
    total = serializers.DecimalField(max_digits=10, decimal_places=2)
    customer_id = serializers.IntegerField()
    order_key = serializers.CharField()
    billing = serializers.DictField()
    shipping = serializers.DictField()
    payment_method = serializers.CharField()
    customer_note = serializers.CharField(required=False, allow_blank=True)
    line_items = serializers.ListField(child=serializers.DictField())

    def validate_status(self, value: str):
        # pending, processing, on-hold, completed, cancelled, refunded, failed and trash
        status_map = {
            "pending": StatusChoices.PENDING,
            "processing": StatusChoices.PENDING,
            "on-hold": StatusChoices.ONHOLD,
            "completed": StatusChoices.COMPLETED,
            "cancelled": StatusChoices.CANCELED,
            "refunded": StatusChoices.DISPUTED,
            "failed": StatusChoices.FAILED,
            "trash": StatusChoices.DRAFT,
        }
        return status_map.get(value, StatusChoices.PENDING)

    def validate_billing(self, value: dict[str, Any]):
        # only add required k:v
        new_val: dict[str, Any] = {}
        new_val["full_name"] = value["first_name"] + " " + value["last_name"]
        new_val["address"] = value["address_1"]
        new_val["phone"] = value["phone"]
        new_val["email"] = value["email"]
        return new_val

    def validate_shipping(self, value: dict[str, str]):
        new_val: dict[str, str] = {}
        new_val["address"] = value["address_1"]
        new_val["phone2"] = value["phone"]
        new_val["delivery_ncm_to"] = WC_NCM_MAP.get(value["state"], "")
        return new_val

    def validate_payment_method(self, value: str):
        if value in ["e", "esewa", "eSewa"]:
            return PaymentMethodChoices.ESEWA_PERSONAL
        if value == "cod":
            return PaymentMethodChoices.COD
        return PaymentMethodChoices.COD

    def validate_line_items(
        self, value: list[dict[str, Any]]
    ) -> list[dict[str, str]]:
        new_value: list[dict[str, Any]] = []
        for item in value:
            new_item: dict[str, Any] = {}
            new_item["id"] = item["id"]
            new_item["product_id"] = item["product_id"]
            new_item["name"] = item["name"]
            new_item["quantity"] = item["quantity"]
            # float to Decimal, 2 decimal_places
            new_item["subtotal"] = Decimal(item["subtotal"]).quantize(
                Decimal(".01"), rounding=ROUND_HALF_UP
            )
            new_item["price"] = Decimal(item["total"]).quantize(
                Decimal(".01"), rounding=ROUND_HALF_UP
            )
            # discount is not directly given
            new_item["discount"] = new_item["subtotal"] - new_item["price"]
            # per unit price same as subtotal if quantity = 1
            new_item["price_per_unit"] = new_item["subtotal"]
            if new_item["quantity"] > 1:
                # per unit price calculated by subtotal / quantity
                new_item["price_per_unit"] = (
                    new_item["subtotal"] / new_item["quantity"]
                )
            for data in item["meta_data"]:
                if data["key"] == "pa_include-longsleeve":
                    new_item["include_longsleeve"] = data["value"] == "yes"
                elif data["key"] == "pa_size":
                    sizes_map = {
                        "s": SizeChoices.S,
                        "m": SizeChoices.M,
                        "l": SizeChoices.L,
                        "xl": SizeChoices.XL,
                        "xxl": SizeChoices.XXL,
                        "3xl": SizeChoices.XXXL,
                        "free-size": SizeChoices.FREE,
                    }
                    new_item["size"] = sizes_map.get(
                        data["value"], SizeChoices.FREE
                    )
                elif data["key"] == "pa_minimal-logo-variation":
                    logos_map = {
                        "rzzy": LogoVariationChoices.RZZY,
                        "attack-on-titan": LogoVariationChoices.AOT,
                        "onepiece3d2y": LogoVariationChoices.OP3D2Y,
                        "berserk": LogoVariationChoices.BERSERK,
                    }
                    new_item["logo_variation"] = logos_map.get(
                        data["value"], LogoVariationChoices.DEFAULT
                    )
                elif data["key"] == "pa_color":
                    colors_map = {
                        "black": ColorChoices.BLACK,
                        "white": ColorChoices.WHITE,
                    }
                    new_item["color"] = colors_map.get(
                        data["value"], ColorChoices.BLACK
                    )
            new_value.append(new_item)
        return new_value
