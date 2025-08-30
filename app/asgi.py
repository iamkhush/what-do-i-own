import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")

original_application = get_asgi_application()


async def application(scope, receive, send):
    if scope["type"] == "http":
        scope["root_path"] = os.environ.get("SCRIPT_NAME", "")
    await original_application(scope, receive, send)
