from django.db import models

class User(models.Model):
    name = models.TextField()

    def __str__(self) -> str:
        return self.name