from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from core.serializers import WcNewOrderSerializer
from core import models


class WcOrderView(APIView):
    '''Wc Woocommerce Order View'''
    # ! This will not be authenticated
    # ! validate 'secret' hash to header/body (refer Wc webhook docs)
    permission_classes = [IsAuthenticated]

    def post(self, request):
        wc_serializer = WcNewOrderSerializer(data=request.data)
        wc_serializer.is_valid(raise_exception=True)
        wc_data = wc_serializer.validated_data

        # check if order already exists
        if models.Order.objects.filter(
                medium=models.MediumChoices.WEBSITE, medium_order_id=wc_data['id']).exists():
            return Response({'detail': 'Order already exists'}, status=status.HTTP_409_CONFLICT)

        with transaction.atomic():
            # get or create customer
            customer, created = models.Customer.objects.get_or_create(
                phone=wc_data['billing']['phone'],
            )
            if created:
                customer.full_name = wc_data['billing']['full_name']
                customer.email = wc_data['billing']['email']
                customer.address = wc_data['billing']['address']
                if 'phone2' in wc_data['shipping']:
                    customer.phone2 = wc_data['shipping']['phone2']
                customer.save()

            # get or create category
            category, _ = models.Category.objects.get_or_create(
                title="UNKNOWN")

            # create order
            order = models.Order.objects.create(
                customer=customer,
                medium=models.MediumChoices.WEBSITE,
                medium_order_id=wc_data['id'],
                wc_order_key=wc_data['order_key'],
                status=wc_data['status'],
                subtotal_price=wc_data['total'] -
                wc_data['discount_total'] - wc_data['shipping_total'],
                delivery_charge=wc_data['shipping_total'],
                discount=wc_data['discount_total'],
                total_price=wc_data['total'],
                customer_note=wc_data['customer_note'],
                delivery_to=wc_data['shipping']['address'],
                delivery_note=wc_data['customer_note'],
                ordered_at=wc_data['date_created']
            )

            # get or create product & order_item, for each line_item
            # TODO bulk create
            for item in wc_data['line_items']:
                # product
                product = models.Product.objects.filter(
                    title=item['name'])
                if not product.exists():
                    product = models.Product(
                        title=item['name'],
                        category=category
                    )
                else:
                    product = product.first()
                product.price = item['price_per_unit']
                product.medium_product_id = item['product_id']
                product.save()

                # order item
                order_item = models.OrderItem(
                    product=product,
                    order=order,
                    medium_item_id=item['id'],
                    quantity=item['quantity'],
                    price_per_unit=item['price_per_unit'],
                    discount=item['discount'],
                    price=item['price']
                )
                if item.get('size'):
                    order_item.size = item['size']
                if item.get('color'):
                    order_item.color = item['color']
                if item.get('include_longsleeve'):
                    order_item.include_longsleeve = item['include_longsleeve']
                if item.get('logo_variation'):
                    order_item.logo_variation = item['logo_variation']
                order_item.save()

        return Response({'detail': 'Order created'}, status=status.HTTP_201_CREATED)
