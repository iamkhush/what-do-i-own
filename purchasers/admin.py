from django import forms
from django.contrib import admin

from purchases.models import PurchaseLineItem

from .models import Purchaser


class PurchaseLineItemForm(forms.ModelForm):
    month = forms.DateField(widget=forms.SelectDateWidget)

    class Meta:
        model = PurchaseLineItem
        fields = "__all__"


class PurchaselineItemAdmin(admin.TabularInline):
    model = PurchaseLineItem
    form = PurchaseLineItemForm
    extra = 0
    fields = ("purchase", "quantity", "price", "month")
    ordering = ("-order__purchase_date",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        month = request.GET.get("month")
        if month:
            qs = qs.filter(order__purchase_date__month=month)
        return qs


class PurchaserAdmin(admin.ModelAdmin):
    inlines = [
        PurchaselineItemAdmin,
    ]


admin.site.register(Purchaser, PurchaserAdmin)
