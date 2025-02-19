# views.py

import io
import json
import logging

from django.conf import settings
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from google import genai
from google.genai import types
from PIL import Image
from pydantic import TypeAdapter, ValidationError

from .forms import ImageUploadForm
from .handle_order_input import handle_order_input
from .models import Order

logger = logging.getLogger(__name__)

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
    if request.method == "POST":
        form = ImageUploadForm(request.POST, request.FILES)
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        if form.is_valid():
            image = form.cleaned_data["image"]
            # Save the image file
            image_path = default_storage.save(f"uploads/{image.name}", image)
            # Read the image file
            image_data = image.read()

            # Change the quality of the image
            image.seek(0)
            pil_image = Image.open(image)
            buffer = io.BytesIO()
            pil_image.save(buffer, format="JPEG", optimize=True, quality=50)
            image_data = buffer.getvalue()

            # Log the file size of the resized image
            resized_image_size = len(image_data)
            logger.debug(f"Resized image size: {resized_image_size} bytes")

            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[
                    prompt,
                    types.Part.from_bytes(data=image_data, mime_type="image/jpeg"),
                ],
                config={
                    "response_mime_type": "application/json",
                    "response_schema": Order,
                },
            )
            logger.debug(f"Full Gemini API Response: {response.text}")  # Debugging
            try:
                json_data = json.loads(response.text)
                logger.debug(f"JSON Data received from Gemini: {json_data}")

                # Attempt to validate and convert with Pydantic:
                try:
                    # Convert the JSON into Python objects using TypeAdapter.
                    order = TypeAdapter(Order).validate_python(json_data)
                    purchase_order = handle_order_input(order)
                    # Get the admin URL for the newly created PurchaseOrder
                    admin_url = reverse(
                        "admin:purchases_purchaseorder_change", args=[purchase_order.id]
                    )
                    # Redirect the user to the admin URL
                    return redirect(admin_url)

                except ValidationError as e:
                    logger.error(f"Pydantic Validation Error: {e}")
                    return JsonResponse(
                        {"error": f"Pydantic Validation Error: {e}"}, status=400
                    )

            except json.JSONDecodeError as e:
                logger.error(f"JSON Decode Error: {e}")
                return JsonResponse(
                    {"error": f"Invalid JSON response from Gemini: {e}"}, status=500
                )
            # if response.status_code == 200:
            #     result = response.json()
            #     # Process the result as needed
            #     return JsonResponse(result)
            # else:
            #     print(response)
            #     return JsonResponse({'error': 'Failed to process image with OpenAI API'}, status=500)
    else:
        form = ImageUploadForm()
    return render(request, "upload.html", {"form": form})
