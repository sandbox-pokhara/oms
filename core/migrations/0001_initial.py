# Generated by Django 5.0.6 on 2024-06-02 10:27

import django.db.models.deletion
import django.utils.timezone
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=255, unique=True)),
                ('description', models.TextField(blank=True, default='')),
                ('image_url', models.URLField(blank=True, default='', max_length=255)),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='Color',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(choices=[('Black', 'Black'), ('White', 'White')], max_length=5)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('full_name', models.CharField(max_length=255)),
                ('gender', models.CharField(blank=True, choices=[('Male', 'Male'), ('Female', 'Female'), ('Unknown', 'Unknown')], default='Unknown', max_length=7)),
                ('insta_handle', models.CharField(blank=True, default='', max_length=255)),
                ('email', models.EmailField(blank=True, default='', max_length=255)),
                ('phone', models.CharField(max_length=15, unique=True)),
                ('phone2', models.CharField(blank=True, default='', max_length=15)),
                ('phone3', models.CharField(blank=True, default='', max_length=15)),
                ('address', models.CharField(blank=True, default='', max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Size',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(choices=[('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'Xl'), ('XXL', 'Xxl'), ('XXXL', 'Xxxl'), ('Free', 'Free')], max_length=4)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('medium', models.CharField(choices=[('Website', 'Website'), ('Instagram', 'Instagram'), ('Contact', 'Contact')], default='Website', max_length=9)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Processed', 'Processed'), ('On Hold', 'Onhold'), ('Shipped', 'Shipped'), ('Delivered', 'Delivered'), ('Canceled', 'Canceled'), ('Disputed', 'Disputed'), ('Completed', 'Completed')], default='Pending', max_length=9)),
                ('subtotal_price', models.DecimalField(decimal_places=2, default=Decimal('5000.00'), max_digits=10)),
                ('delivery_charge', models.DecimalField(decimal_places=2, default=Decimal('150.00'), max_digits=10)),
                ('discount', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10)),
                ('total_price', models.DecimalField(decimal_places=2, default=Decimal('5000.00'), max_digits=10)),
                ('is_paid', models.BooleanField(default=False)),
                ('delivery_from', models.CharField(blank=True, default='Pokhara', max_length=255)),
                ('delivery_to', models.CharField(max_length=255)),
                ('delivery_method', models.CharField(choices=[('NCM', 'Ncm'), ('Aramex', 'Aramex'), ('Self', 'Self'), ('Pathao', 'Pathao'), ('Airport', 'Airport'), ('Zapp', 'Zapp')], default='NCM', max_length=7)),
                ('delivery_note', models.CharField(blank=True, default='', max_length=255)),
                ('delivery_package_id', models.CharField(blank=True, default='', max_length=255)),
                ('ordered_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('shipped_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('delivered_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('paid_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='orders', to='core.customer')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PaymentItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('payment_method', models.CharField(choices=[('COD', 'Cod'), ('Esewa Personal', 'Esewa Personal'), ('Esewa Merchant', 'Esewa Merchant'), ('ebanking', 'Ebanking')], default='COD', max_length=14)),
                ('amount', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10)),
                ('is_advance', models.BooleanField()),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='payment_items', to='core.order')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=255, unique=True)),
                ('description', models.TextField(blank=True, default='')),
                ('image_url', models.URLField(blank=True, default='', max_length=255)),
                ('stock', models.PositiveSmallIntegerField(default=0)),
                ('price', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10)),
                ('available_colors', models.ManyToManyField(blank=True, to='core.color')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='products', to='core.category')),
                ('available_sizes', models.ManyToManyField(blank=True, to='core.size')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_giveaway', models.BooleanField(default=False)),
                ('giveaway_reason', models.CharField(blank=True, default='', max_length=255)),
                ('size', models.CharField(choices=[('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'Xl'), ('XXL', 'Xxl'), ('XXXL', 'Xxxl'), ('Free', 'Free')], default='M', max_length=4)),
                ('color', models.CharField(choices=[('Black', 'Black'), ('White', 'White')], default='Black', max_length=5)),
                ('quantity', models.PositiveSmallIntegerField(default=1)),
                ('include_longsleeve', models.BooleanField(default=False)),
                ('price_per_unit', models.DecimalField(decimal_places=2, default=Decimal('5000.00'), max_digits=10)),
                ('price', models.DecimalField(decimal_places=2, default=Decimal('5000.00'), max_digits=10)),
                ('is_disputed', models.BooleanField(default=False)),
                ('dispute_remarks', models.CharField(blank=True, default='', max_length=255)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='order_items', to='core.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='order_items', to='core.product')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
