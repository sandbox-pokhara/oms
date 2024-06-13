from rest_framework import serializers
from core.models import StatusChoices
from core.models import PaymentMethodChoices
from core.models import SizeChoices
from core.models import LogoVariationChoices
from core.models import ColorChoices
from decimal import Decimal
from decimal import ROUND_HALF_UP


class WcNewOrderSerializer(serializers.Serializer):
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

    def validate_status(self, value):
        # pending, processing, on-hold, completed, cancelled, refunded, failed and trash
        status_map = {
            'pending': StatusChoices.PENDING,
            'processing': StatusChoices.PENDING,
            'on-hold': StatusChoices.ONHOLD,
            'completed': StatusChoices.COMPLETED,
            'cancelled': StatusChoices.CANCELED,
            'refunded': StatusChoices.DISPUTED,
            'failed': StatusChoices.FAILED,
            'trash': StatusChoices.DRAFT
        }
        return status_map.get(value, StatusChoices.PENDING)

    def validate_billing(self, value):
        # only add required k:v
        new_val = {}
        new_val['full_name'] = value['first_name'] + " " + value['last_name']
        new_val['address'] = value['address_1']
        new_val['phone'] = value['phone']
        new_val['email'] = value['email']
        return new_val

    def validate_shipping(self, value):
        new_val = {}
        new_val['address'] = value['address_1']
        new_val['phone2'] = value['phone']
        return new_val

    def validate_payment_method(self, value):
        if value in ['e', 'esewa', 'eSewa']:
            return PaymentMethodChoices.ESEWA_PERSONAL
        if value == 'cod':
            return PaymentMethodChoices.COD
        return PaymentMethodChoices.COD

    def validate_line_items(self, value):
        new_value = []
        for item in value:
            new_item = {}
            new_item['id'] = item['id']
            new_item['product_id'] = item['product_id']
            new_item['name'] = item['name']
            new_item['quantity'] = item['quantity']
            # float to Decimal, 2 decimal_places
            new_item['subtotal'] = Decimal(item['subtotal']).quantize(
                Decimal('.01'), rounding=ROUND_HALF_UP)
            new_item['price'] = Decimal(item['total']).quantize(
                Decimal('.01'), rounding=ROUND_HALF_UP)
            # discount is not directly given
            new_item['discount'] = new_item['subtotal'] - new_item['price']
            # per unit price same as subtotal if quantity = 1
            new_item['price_per_unit'] = new_item['subtotal']
            if new_item['quantity'] > 1:
                # per unit price calculated by subtotal / quantity
                new_item['price_per_unit'] = new_item['subtotal'] / \
                    new_item['quantity']
            for data in item['meta_data']:
                if data['key'] == 'pa_include-longsleeve':
                    new_item['include_longsleeve'] = data['value'] == 'yes'
                elif data['key'] == 'pa_size':
                    sizes_map = {
                        's': SizeChoices.S,
                        'm': SizeChoices.M,
                        'l': SizeChoices.L,
                        'xl': SizeChoices.XL,
                        'xxl': SizeChoices.XXL,
                        '3xl': SizeChoices.XXXL,
                        'free-size': SizeChoices.FREE
                    }
                    new_item['size'] = sizes_map.get(
                        data['value'], SizeChoices.FREE)
                elif data['key'] == 'pa_minimal-logo-variation':
                    logos_map = {
                        'rzzy': LogoVariationChoices.RZZY,
                        'attack-on-titan': LogoVariationChoices.AOT,
                        'onepiece3d2y': LogoVariationChoices.OP3D2Y,
                        'berserk': LogoVariationChoices.BERSERK
                    }
                    new_item['logo_variation'] = logos_map.get(
                        data['value'], LogoVariationChoices.DEFAULT)
                elif data['key'] == 'pa_color':
                    colors_map = {
                        'black': ColorChoices.BLACK,
                        'white': ColorChoices.WHITE
                    }
                    new_item['color'] = colors_map.get(
                        data['value'], ColorChoices.BLACK)
            new_value.append(new_item)
        return new_value
