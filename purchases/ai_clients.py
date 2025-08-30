from google import genai
from google.genai import types


class InvoiceAIClient:
    """Abstracts the AI model interaction for invoice extraction."""

    def __init__(self, api_key, model_name):
        self.api_key = api_key
        self.model_name = model_name

    def extract_invoice(self, prompt, file_data, mime_type, response_schema):
        raise NotImplementedError("Subclasses must implement extract_invoice")


class GeminiInvoiceAIClient(InvoiceAIClient):
    def __init__(self, api_key, model_name):
        super().__init__(api_key, model_name)
        self.client = genai.Client(api_key=api_key)

    def extract_invoice(self, prompt, file_data, mime_type, response_schema):
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=[
                prompt,
                types.Part.from_bytes(data=file_data, mime_type=mime_type),
            ],
            config={
                "response_mime_type": "application/json",
                "response_schema": response_schema,
            },
        )
        return response.text
