# views.py

import json
from datetime import datetime
from typing import Literal
from google import genai
from google.genai import types
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings 
from .forms import ImageUploadForm
from pydantic import BaseModel, TypeAdapter, ValidationError

from .models import PurchaseOrder, PurchaseLineItem
from stores.models import Store
from purchase.models import Purchase
from purchasers.models import Purchaser

class PurchaseModel(BaseModel):
    name: str
    quantity: str
    quantity_unit: Literal["PIECE", "GRAMS" , "MLITRES"]
    price: str


class Order(BaseModel):
    total_paid: float
    purchase_date: str
    store: str
    purchases: list[PurchaseModel]


prompt = """
This is an invoice image.  Extract the following information and return it as a JSON string:

*  **total_paid:** The total amount paid on the invoice.
*  **store:** The name of the store.
*  **purchase_date:** Date of purchase in yyyy-mm-dd format.
*  **purchases:**  A list of individual purchases.  For each purchase, extract:
    *   **name:** The name of the product or service purchased.
    *   **quantity:** The quantity purchased.
    *   **quantity_unit:** The unit of quanity purchased. Can be of the following PIECE, GRAMS and MLITRES. Adjust the quantity accordingly.
    *   **price:** The price per unit of the product or service.

Make sure that all prices are in basis points which means 23.8 becomes 2380.
Ensure the JSON is valid and well-formed.  Do not include any extra text or explanations.
"""


def image_upload_view(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        if form.is_valid():
            image = form.cleaned_data['image']
            # Read the image file
            image_data = image.read()
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[
                    prompt,
                    types.Part.from_bytes(data=image_data, mime_type=image.content_type)
                ],
                config={
                    'response_mime_type': 'application/json',
                    'response_schema' : Order
                }
            )
            print(f"Full Gemini API Response: {response.text}") # Debugging
            try:
                json_data = json.loads(response.text)

                # Attempt to validate and convert with Pydantic:
                try:
                    # Convert the JSON into Python objects using TypeAdapter.
                    order = TypeAdapter(Order).validate_python(json_data)
                    store, _ = Store.objects.get_or_create(name__iexact=order.store)
                    created_at=datetime.strptime(order.purchase_date, '%Y-%m-%d')
                    order_db = PurchaseOrder.objects.create(total=order.total_paid, purchased_at_store=store, purchase_date=created_at)
                    purchases = []
                    purchaser = Purchaser.objects.get(id=1) #ghar
                    for purchase in order.purchases:
                        item, _ = Purchase.objects.get_or_create(name__iexact=purchase.name)
                        actual_unit = 1
                        match purchase.quantity_unit:
                            case 'MLITRES':
                                actual_unit = 3
                            case 'GRAMS':
                                actual_unit = 2
                            case _:
                                actual_unit = 1

                        purchases.append(PurchaseLineItem(order=order_db, 
                                                          price=purchase.price, 
                                                          purchaser=purchaser,
                                                          purchase=item,
                                                          quantity=purchase.quantity,
                                                          quantity_unit=actual_unit))
                    PurchaseLineItem.objects.bulk_create(purchases)
                    # If it's valid, return the JSON
                    form.save()
                    return JsonResponse(json_data)

                except ValidationError as e:
                    print(f"Pydantic Validation Error: {e}")
                    return JsonResponse({"error": f"Pydantic Validation Error: {e}"}, status=400)

            except json.JSONDecodeError as e:
                print(f"JSON Decode Error: {e}")
                return JsonResponse({"error": f"Invalid JSON response from Gemini: {e}"}, status=500)
            # if response.status_code == 200:
            #     result = response.json()
            #     # Process the result as needed
            #     return JsonResponse(result)
            # else:
            #     print(response)
            #     return JsonResponse({'error': 'Failed to process image with OpenAI API'}, status=500)
    else:
        form = ImageUploadForm()
    return render(request, 'upload.html', {'form': form})
