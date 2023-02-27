from django.contrib import admin
from django.db.models import Sum, functions, DateTimeField, Min, Max, Count
from purchases.models import PurchaseOrder, PurchaseLineItem, PurchaseSummary

class PurchaseOrderlineAdmin(admin.TabularInline):
    model = PurchaseLineItem

class PurchaseOrderAdmin(admin.ModelAdmin):
    inlines = [
        PurchaseOrderlineAdmin,
    ]
    list_display = ['purchased_at_store', 'purchase_date', 'order_total']
    date_hierarchy = 'purchase_date'
    ordering = ('-purchase_date',)
    search_fields = ('purchased_at_store',)

    def total(self, obj: PurchaseOrder):
        return obj.price * obj.quantity / 100

class PurchaseSummaryAdmin(admin.ModelAdmin):
    change_list_template = 'admin/purchase_summary_change_list.html'
    date_hierarchy = 'order__purchase_date'

    list_filter = ('user',)

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(
            request,
            extra_context=extra_context,
        )
        try:
            qs = response.context_data["cl"].queryset
        except (AttributeError, KeyError):
            return response
        
        # metrics = {
        #     "total": Sum("quantity"),
        #     "total_purchases": Sum("price")/100,
        # }
        # response.context_data["summary"] = list(
        #     qs
        #     .annotate(**metrics)
        #     .order_by("-total_purchases")
        # )

        summary_over_time = qs.values('user__name',).annotate(
            total=Sum('price')/100,
            purchase_count=Count('user__name')).order_by('-purchase_count')
        
        summary_range = summary_over_time.aggregate(
            low=Min('total'),
            high=Max('total'),
        )
        high = summary_range.get('high', 0)
        low = summary_range.get('low', 0)
        response.context_data['summary_over_time'] = [{
            'total': x['total'] or 0,
            'pct': \
               ((x['total'] or 0) - low) / (high - low) * 100 
               if high > low else 0,
            'user': x['user__name']
        } for x in summary_over_time]

        print(response.context_data['summary_over_time'])
        
        return response

admin.site.register(PurchaseOrder, PurchaseOrderAdmin)
admin.site.register(PurchaseSummary, PurchaseSummaryAdmin)