# Generated by Django 5.1.4 on 2025-01-10 21:23

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("purchase", "0001_initial"),
        ("purchasers", "0001_initial"),
        ("stores", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="PurchaseLineItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("price", models.BigIntegerField(default=0)),
                ("quantity", models.IntegerField(default=1)),
                (
                    "purchase",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="purchase.purchase",
                    ),
                ),
                (
                    "purchaser",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="purchasers.purchaser",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PurchaseSummary",
            fields=[],
            options={
                "verbose_name": "Purchase Summary",
                "verbose_name_plural": "Purchases Summary",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("purchases.purchaselineitem",),
        ),
        migrations.CreateModel(
            name="PurchaseOrder",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("purchase_date", models.DateField(default=django.utils.timezone.now)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "purchased_at_store",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="stores.store"
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="purchaselineitem",
            name="order",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="line_items",
                to="purchases.purchaseorder",
            ),
        ),
    ]
