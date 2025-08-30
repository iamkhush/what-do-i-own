# views.py

import io
import json
import logging
from datetime import date, datetime

from django.conf import settings
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from google import genai
from google.genai import types
from PIL import Image
from pydantic import TypeAdapter, ValidationError

from .ai_clients import GeminiInvoiceAIClient, InvoiceAIClient
from .forms import ImageUploadForm
from .handle_order_input import handle_order_input
from .models import Order, PurchaseOrder

logger = logging.getLogger(__name__)

prompt = """
This is an invoice image.  Extract the following information and return it as a JSON string:

*  **total_paid:** The total amount paid on the invoice in basis points.
*  **store:** The name of the store.
*  **purchase_date:** Date of purchase in yyyy-mm-dd format.
*  **purchases:**  A list of individual purchases. For each purchase, extract:
    *   **name:** The name of the product or service purchased. 
    *   **quantity:** The quantity purchased.
    *   **quantity_unit:** The unit of quantity purchased. Can be of the following PIECE, GRAMS and MLITRES. Adjust the quantity accordingly.
    *   **price:** The price per unit. To calculate, take the item's list price and subtract the monetary value of any discount, which may be listed on the following line, ignoring the discount's text description.

Make sure that all prices are in basis points which means 23.8 becomes 2380.
Ensure the JSON is valid and well-formed. Do not include any extra text or explanations.
"""


def get_invoice_ai_client():
    # You can easily switch to another AI client here if needed
    return GeminiInvoiceAIClient(
        api_key=settings.GEMINI_API_KEY,
        model_name=getattr(settings, "AI_MODEL_NAME", "gemini-2.5-flash-lite"),
    )


def image_upload_view(request):
    if request.method == "POST":
        form = ImageUploadForm(request.POST, request.FILES)
        ai_client = get_invoice_ai_client()
        if form.is_valid():
            uploaded_file = form.cleaned_data["file"]
            file_extension = uploaded_file.name.split(".")[-1].lower()
            binary_data = uploaded_file.read()
            today = datetime.today()
            year = today.strftime("%Y")
            month = today.strftime("%m")
            today_str = today.strftime("%Y-%m-%d")
            filename = f"uploads/{year}/{month}/{today_str}_{uploaded_file.name}"
            default_storage.save(filename, uploaded_file)
            if file_extension in ["jpg", "jpeg", "png"]:
                # Change the quality of the image
                uploaded_file.seek(0)
                pil_image = Image.open(uploaded_file)
                buffer = io.BytesIO()
                pil_image.save(buffer, format="JPEG", optimize=True, quality=50)
                file_data = buffer.getvalue()
                mime_type = "image/jpeg"
            elif file_extension == "pdf":
                # Handle PDF file
                file_data = binary_data
                mime_type = "application/pdf"
            else:
                return JsonResponse({"error": "Unsupported file type"}, status=400)

            # Log the file size of the resized image or PDF text
            file_size = len(file_data)
            logger.debug(f"Uploaded file size: {file_size} bytes")

            ai_response = ai_client.extract_invoice(
                prompt=prompt,
                file_data=file_data,
                mime_type=mime_type,
                response_schema=Order,
            )
            logger.debug(f"Full AI API Response: {ai_response}")
            try:
                json_data = json.loads(ai_response)
            except json.JSONDecodeError as e:
                logger.error(f"JSON Decode Error: {e}")
                return JsonResponse(
                    {"error": f"Invalid JSON response from AI: {e}"}, status=500
                )
            logger.debug(f"JSON Data received from AI: {json_data}")

            try:
                order = TypeAdapter(Order).validate_python(json_data)
                purchase_order = handle_order_input(order)
                admin_url = reverse(
                    "admin:purchases_purchaseorder_change", args=[purchase_order.id]
                )
                return redirect(admin_url)
            except ValidationError as e:
                logger.error(f"Pydantic Validation Error: {e}")
                return JsonResponse(
                    {"error": f"Pydantic Validation Error: {e}"}, status=400
                )
    else:
        form = ImageUploadForm()
    return render(
        request,
        "upload.html",
        {
            "form": form,
            "ai_model_name": getattr(
                settings, "GEMINI_AI_MODEL_NAME", "gemini-2.5-flash-lite"
            ),
        },
    )


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)


def monthly_summary(request):
    summary = PurchaseOrder.get_monthly_summary()
    data = list(summary.values("month", "purchaser__name", "total"))
    data_json = json.dumps(data, cls=DateEncoder)
    return render(request, "monthly_summary.html", {"data": data_json})
