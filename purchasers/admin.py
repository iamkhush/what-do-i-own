from django.contrib import admin

from purchasers.models import Purchaser


class PurchaserAdmin(admin.ModelAdmin):
    pass


admin.site.register(Purchaser, PurchaserAdmin)
