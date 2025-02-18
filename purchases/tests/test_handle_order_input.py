from datetime import datetime

from django.test import TestCase

from purchasers.models import Purchaser
from purchases.handle_order_input import handle_order_input
from purchases.models import Order, PurchaseLineItem, PurchaseModel, PurchaseOrder
from stores.models import Store


class HandleOrderInputTest(TestCase):
    def setUp(self):
        self.purchaser = Purchaser.objects.create(id=1, name="Test Purchaser")

    def test_handle_order_input_creates_database_rows(self):
        sample_order = Order(
            total_paid=100.0,
            purchase_date="2023-10-01",
            store="Test Store",
            purchases=[
                PurchaseModel(
                    name="Test Product 1", quantity=2, quantity_unit="PIECE", price=50
                ),
                PurchaseModel(
                    name="Test Product 2", quantity=500, quantity_unit="GRAMS", price=25
                ),
            ],
        )

        handle_order_input(sample_order)

        # Check if the store was created
        store = Store.objects.get(name__iexact="Test Store")
        self.assertIsNotNone(store)

        # Check if the purchase order was created
        purchase_order = PurchaseOrder.objects.get(purchased_at_store=store)
        self.assertIsNotNone(purchase_order)
        self.assertEqual(purchase_order.total, 100.0)
        self.assertEqual(
            purchase_order.purchase_date,
            datetime.strptime("2023-10-01", "%Y-%m-%d").date(),
        )

        # Check if the purchase line items were created
        purchase_line_items = PurchaseLineItem.objects.filter(order=purchase_order)
        self.assertEqual(purchase_line_items.count(), 2)

        # Check details of the first purchase line item
        purchase_line_item_1 = purchase_line_items.get(
            purchase__name__iexact="Test Product 1"
        )
        self.assertEqual(purchase_line_item_1.quantity, 2)
        self.assertEqual(purchase_line_item_1.quantity_unit, 1)
        self.assertEqual(purchase_line_item_1.price, 50)

        # Check details of the second purchase line item
        purchase_line_item_2 = purchase_line_items.get(
            purchase__name__iexact="Test Product 2"
        )
        self.assertEqual(purchase_line_item_2.quantity, 500)
        self.assertEqual(purchase_line_item_2.quantity_unit, 2)
        self.assertEqual(purchase_line_item_2.price, 25)
