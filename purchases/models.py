from django.db import models
from django.contrib import admin
from django.utils import timezone
from django.db.models import Sum

from users.models import User

class PurchaseCategories(models.IntegerChoices):
        CLOTHES = 1
        FOOD = 2
        SERVICES = 3
        HEALTH = 4
        MISCELLANEOUS = 5


class PurchaseOrder(models.Model):
    purchase_date = models.DateField(default=timezone.now)
    purchased_at_store = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
         return f'{self.purchased_at_store}'
    
    @admin.display(description='Order Total')
    def order_total(self):
        return self.line_items.all().aggregate(Sum('price'))['price__sum'] / 100
    
class PurchaseLineItem(models.Model):
    price = models.BigIntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='line_items')
    quantity = models.IntegerField(default=1)
    name = models.TextField(null=True)
    category = models.IntegerField(choices=PurchaseCategories.choices)

    @property
    def price_in_units(self):
        return self.price / 100

    # @property
    # def total(self):
    #     return self.price_in_units * self.quantity


class PurchaseSummary(PurchaseLineItem):
    class Meta:
        proxy = True
        verbose_name = "Purchase Summary"
        verbose_name_plural = "Purchases Summary"