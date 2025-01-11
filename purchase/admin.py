from django.contrib import admin
from purchases.models import PurchaseLineItem, QuantityUnit
from purchase.models import Purchase

class PurchasesLineItemAdmin(admin.TabularInline):
    model = PurchaseLineItem
    readonly_fields = ('purchaser', 'order', 'price_per_unit')
    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
 
    def price_per_unit(self, obj):
        if obj.quantity_unit == QuantityUnit.GRAMS:
            return f'SEK {obj.price * 10 / obj.quantity:.2f} per kg'
        return f'SEK {obj.price / (obj.quantity * 100)} per piece'

class PurchaseAdmin(admin.ModelAdmin):
    inlines = [PurchasesLineItemAdmin]
    list_display = ['name', 'category', 'bought_count']
    search_fields = ('name',)

    def bought_count(self, obj):
        return obj.line_items.count()

admin.site.register(Purchase, PurchaseAdmin)
