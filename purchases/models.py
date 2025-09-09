from typing import Literal

from django.contrib import admin
from django.db import models
from django.db.models import F, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from pydantic import BaseModel

from purchase.models import Purchase
from purchasers.models import Purchaser
from stores.models import Store


class QuantityUnit(models.IntegerChoices):
    PIECE = 1
    GRAMS = 2
    MLITRES = 3


class PurchaseOrder(models.Model):
    purchase_date = models.DateField(default=timezone.now)
    purchased_at_store = models.ForeignKey(Store, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.BigIntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.purchased_at_store}"

    @staticmethod
    def get_monthly_summary():
        return (
            PurchaseLineItem.objects.annotate(month=TruncMonth("order__purchase_date"))
            .values("month", "purchaser__name")
            .annotate(total=Sum(F("price") * F("quantity")) / 100)
            .order_by("month", "purchaser__name")
        )


class PurchaseLineItem(models.Model):
    price = models.BigIntegerField(default=0)  # this is price per unit in basis points
    purchaser = models.ForeignKey(Purchaser, on_delete=models.PROTECT)
    order = models.ForeignKey(
        PurchaseOrder, on_delete=models.CASCADE, related_name="line_items"
    )
    quantity = models.IntegerField(default=1)
    quantity_unit = models.IntegerField(
        choices=QuantityUnit, default=QuantityUnit.PIECE
    )
    purchase = models.ForeignKey(
        Purchase, on_delete=models.PROTECT, related_name="line_items"
    )

    @property
    def price_in_units(self):
        return self.price / 100

    def __str__(self) -> str:
        return f"Line item in {self.order} purchase on {self.order.created_at.strftime('%d %B %Y')}"

    # @property
    # def total(self):
    #     return self.price_in_units * self.quantity


class PurchaseSummary(PurchaseLineItem):
    class Meta:
        proxy = True
        verbose_name = "Purchase Summary"
        verbose_name_plural = "Purchases Summary"


class PurchaseModel(BaseModel):
    name: str
    quantity: int
    quantity_unit: Literal["PIECE", "GRAMS", "MLITRES"]
    price: int


class Order(BaseModel):
    total_paid: int
    purchase_date: str
    store: str
    purchases: list[PurchaseModel]
