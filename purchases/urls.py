# urls.py

from django.urls import path

from .views import image_upload_view, monthly_summary

urlpatterns = [
    path("upload/", image_upload_view, name="image_upload"),
    path("", monthly_summary, name="summary"),
    # Add other URLs as needed
]
