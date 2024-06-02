from django.db import models
from functools import partial
from decimal import Decimal

from django.utils import timezone


class Gender(models.TextChoices):
    MALE = 'Male'
    FEMALE = 'Female'
    UNKNOWN = 'Unknown'


class SizeChoices(models.TextChoices):
    S = 'S'
    M = 'M'
    L = 'L'
    XL = 'XL'
    XXL = 'XXL'
    XXXL = 'XXXL'
    FREE = 'Free'


class ColorChoices(models.TextChoices):
    BLACK = 'Black'
    WHITE = 'White'


class StatusChoices(models.TextChoices):
    PENDING = 'Pending'
    PROCESSED = 'Processed'
    ONHOLD = 'On Hold'
    SHIPPED = 'Shipped'
    DELIVERED = 'Delivered'
    CANCELED = 'Canceled'
    DISPUTED = 'Disputed'
    COMPLETED = 'Completed'


class DeliveryMethodChoices(models.TextChoices):
    NCM = 'NCM'
    ARAMEX = 'Aramex'
    SELF = 'Self'
    PATHAO = 'Pathao'
    AIRPORT = 'Airport'
    ZAPP = 'Zapp'


class MediumChoices(models.TextChoices):
    WEBSITE = 'Website'
    INSTAGRAM = 'Instagram'
    CONTACT = 'Contact'


class PaymentMethodChoices(models.TextChoices):
    COD = 'COD'
    ESEWA_PERSONAL = 'Esewa Personal'
    ESEWA_MERCHANT = 'Esewa Merchant'
    EBANKING = 'ebanking'


class LogoChoices(models.TextChoices):
    RZZY = 'Rzzy'
    AOT = 'Attack On Titan'
    OP3D2Y = 'Onepiece 3D2Y'
    BERSERK = 'Berserk'


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


OptionalCharField = partial(
    models.CharField, max_length=255, blank=True, default='')
OptionalTextField = partial(
    models.TextField, blank=True, default='')
OptionalEmailField = partial(
    models.EmailField, max_length=255, blank=True, default='')
OptionalURLField = partial(
    models.URLField, max_length=255, blank=True, default='')
OptionalDateTimeField = partial(
    models.DateTimeField, blank=True, null=True, default=None)
AmountField = partial(models.DecimalField, max_digits=10,
                      decimal_places=2, default=Decimal('5000.00'))


class Customer(TimestampedModel):
    full_name = models.CharField(max_length=255)
    gender = OptionalCharField(
        max_length=7, choices=Gender.choices, default=Gender.UNKNOWN)
    # instagram username
    insta_handle = OptionalCharField()
    email = OptionalEmailField()
    # three contact numbers (primary is UNIQUE)
    phone = models.CharField(max_length=15, unique=True)
    phone2 = OptionalCharField(max_length=15)
    phone3 = OptionalCharField(max_length=15)
    # Home Address of the customer, may not be the Shipping Address
    address = OptionalCharField()


class Category(TimestampedModel):
    title = models.CharField(max_length=255, unique=True)
    description = OptionalTextField()
    image_url = OptionalURLField()

    class Meta:
        verbose_name_plural = 'Categories'


class Size(TimestampedModel):
    name = models.CharField(max_length=4, choices=SizeChoices.choices)


class Color(TimestampedModel):
    name = models.CharField(max_length=5, choices=ColorChoices.choices)


class Product(TimestampedModel):
    title = models.CharField(max_length=255, unique=True)
    description = OptionalTextField()
    image_url = OptionalURLField()
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name='products')
    # available sizes = S, M, L, XL, ...
    available_sizes = models.ManyToManyField(Size, blank=True)
    # available colors = Black, White, ...
    available_colors = models.ManyToManyField(Color, blank=True)
    # current stock number, 0 = out of stock
    stock = models.PositiveSmallIntegerField(default=0)
    price = AmountField(default=Decimal('0.00'))


class Order(TimestampedModel):
    customer = models.ForeignKey(
        Customer, on_delete=models.PROTECT, related_name='orders')
    medium = models.CharField(
        max_length=9, choices=MediumChoices.choices, default=MediumChoices.WEBSITE)
    status = models.CharField(
        max_length=9, choices=StatusChoices.choices, default=StatusChoices.PENDING)
    subtotal_price = AmountField()
    delivery_charge = AmountField(default=Decimal('150.00'))
    discount = AmountField(default=Decimal('0.00'))
    # grand total
    total_price = AmountField()
    is_paid = models.BooleanField(default=False)
    # delivery to/from addresses
    delivery_from = OptionalCharField(default='Pokhara')
    delivery_to = models.CharField(max_length=255)
    delivery_method = models.CharField(
        max_length=7, choices=DeliveryMethodChoices.choices, default=DeliveryMethodChoices.NCM)
    # note for delivery company
    delivery_note = OptionalCharField()
    # unique package ids from delivery companies/services
    delivery_package_id = OptionalCharField()
    # (optional)dates to keep track
    # ordered_at: same as created_at, except for old orders(Notion)
    ordered_at = models.DateTimeField(default=timezone.now)
    shipped_at = OptionalDateTimeField()
    delivered_at = OptionalDateTimeField()
    paid_at = OptionalDateTimeField()   # full payment


class PaymentItem(TimestampedModel):
    # one order can have one or more payments (Installments, Full)
    order = models.ForeignKey(
        Order, on_delete=models.PROTECT, related_name='payment_items')
    payment_method = models.CharField(
        max_length=14, choices=PaymentMethodChoices.choices, default=PaymentMethodChoices.COD)
    amount = AmountField(default=Decimal('0.00'))
    # is advance payment or not?
    # if False, then it denotes full payment/ last of the installments
    is_advance = models.BooleanField()


class OrderItem(TimestampedModel):
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name='order_items')
    order = models.ForeignKey(
        Order, on_delete=models.PROTECT, related_name='order_items')
    # giveaway OrderItem's price will not contribute in Order's total price
    # those Orders might have total price=0.00, and no payment items
    is_giveaway = models.BooleanField(default=False)
    giveaway_reason = OptionalCharField()
    size = models.CharField(
        max_length=4, choices=SizeChoices.choices, default=SizeChoices.M)
    color = models.CharField(
        max_length=5, choices=ColorChoices.choices, default=ColorChoices.BLACK)
    # quantity of same product ordered
    quantity = models.PositiveSmallIntegerField(default=1)
    # added charge for including longsleeve
    include_longsleeve = models.BooleanField(default=False)
    # price of a single product
    price_per_unit = AmountField()
    # price for all products
    price = AmountField()
    # if the item is disputed(request for return/exchange/refund)
    is_disputed = models.BooleanField(default=False)
    # remarks, eg. 'defect, product exchanged'
    dispute_remarks = OptionalCharField()
