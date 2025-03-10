from django.db import models


class PurchaseCategories(models.IntegerChoices):
    CLOTHES = 1
    FOOD = 2
    SERVICES = 3
    HEALTH = 4
    MISCELLANEOUS = 5
    HOUSEHOLD = 6


class Purchase(models.Model):
    name = models.TextField(null=True, unique=True)
    category = models.IntegerField(
        choices=PurchaseCategories.choices, default=PurchaseCategories.FOOD
    )

    class Meta:
        ordering = ["-name"]

    def __str__(self) -> str:
        return f"{self.name}"
