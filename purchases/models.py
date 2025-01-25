from django.db import models
from django.contrib import admin
from django.utils import timezone
from django.db.models import Sum

from purchasers.models import Purchaser
from purchase.models import Purchase
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
         return f'{self.purchased_at_store}'
    
class PurchaseLineItem(models.Model):
    price = models.BigIntegerField(default=0)
    purchaser = models.ForeignKey(Purchaser, on_delete=models.PROTECT)
    order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='line_items')
    quantity = models.IntegerField(default=1)
    quantity_unit = models.IntegerField(choices=QuantityUnit, default=QuantityUnit.PIECE)
    purchase = models.ForeignKey(Purchase, on_delete=models.PROTECT, related_name='line_items')

    @property
    def price_in_units(self):
        return self.price / 100
    
    def __str__(self) -> str:
         return f'Line item in {self.order} purchase on {self.order.created_at.strftime('%d %B %Y')}'

    # @property
    # def total(self):
    #     return self.price_in_units * self.quantity


class PurchaseSummary(PurchaseLineItem):
    class Meta:
        proxy = True
        verbose_name = "Purchase Summary"
        verbose_name_plural = "Purchases Summary"