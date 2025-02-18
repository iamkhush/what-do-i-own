from datetime import datetime

from purchase.models import Purchase
from purchasers.models import Purchaser
from stores.models import Store

from .models import Order, PurchaseLineItem, PurchaseOrder


def handle_order_input(order: Order) -> None:
    store, _ = Store.objects.get_or_create(
        name__iexact=order.store, defaults={"name": order.store}
    )
    created_at = datetime.strptime(order.purchase_date, "%Y-%m-%d")
    order_db = PurchaseOrder.objects.create(
        total=order.total_paid, purchased_at_store=store, purchase_date=created_at
    )
    purchases = []
    purchaser = Purchaser.objects.get(id=1)  # ghar
    for purchase in order.purchases:
        item, _ = Purchase.objects.get_or_create(
            name__iexact=purchase.name, defaults={"name": purchase.name}
        )
        actual_unit = 1
        match purchase.quantity_unit:
            case "MLITRES":
                actual_unit = 3
            case "GRAMS":
                actual_unit = 2
            case _:
                actual_unit = 1

        purchases.append(
            PurchaseLineItem(
                order=order_db,
                price=purchase.price,
                purchaser=purchaser,
                purchase=item,
                quantity=purchase.quantity,
                quantity_unit=actual_unit,
            )
        )
    PurchaseLineItem.objects.bulk_create(purchases)
