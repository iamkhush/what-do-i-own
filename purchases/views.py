# views.py

import json
from google import genai
from google.genai import types
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings

from .handle_order_input import handle_order_input 
from .forms import ImageUploadForm
from pydantic import TypeAdapter, ValidationError




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
                    handle_order_input(order)
                    # If it's valid, return the JSON
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
