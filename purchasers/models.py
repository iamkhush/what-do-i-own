from django.db import models


class Purchaser(models.Model):
    name = models.TextField(unique=True)

    def __str__(self) -> str:
        return self.name
