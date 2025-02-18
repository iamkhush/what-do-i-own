from django.contrib import admin
from django.db.models import Count, DateTimeField, Max, Min, Sum, functions

from purchases.models import PurchaseLineItem, PurchaseOrder, PurchaseSummary


class PurchaseOrderlineAdmin(admin.TabularInline):
    model = PurchaseLineItem


class PurchaseOrderAdmin(admin.ModelAdmin):
    inlines = [
        PurchaseOrderlineAdmin,
    ]
    list_display = ["purchased_at_store", "purchase_date", "total_formatted"]
    date_hierarchy = "purchase_date"
    ordering = ("-purchase_date",)
    search_fields = ("purchased_at_store",)

    def total_formatted(self, obj: PurchaseOrder):
        return obj.total / 100


class PurchaseSummaryAdmin(admin.ModelAdmin):
    change_list_template = "admin/purchase_summary_change_list.html"
    date_hierarchy = "order__purchase_date"

    list_filter = ("purchaser",)

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

        summary_over_time = (
            qs.values(
                "purchaser__name",
            )
            .annotate(total=Sum("price") / 100, purchase_count=Count("purchaser__name"))
            .order_by("-purchase_count")
        )

        summary_range = summary_over_time.aggregate(
            low=Min("total"),
            high=Max("total"),
        )
        high = summary_range.get("high", 0)
        low = summary_range.get("low", 0)
        response.context_data["summary_over_time"] = [
            {
                "total": x["total"] or 0,
                "pct": ((x["total"] or 0) - low) / (high - low) * 100
                if high > low
                else 0,
                "purchaser": x["purchaser__name"],
            }
            for x in summary_over_time
        ]

        print(response.context_data["summary_over_time"])

        return response


admin.site.register(PurchaseOrder, PurchaseOrderAdmin)
admin.site.register(PurchaseSummary, PurchaseSummaryAdmin)
