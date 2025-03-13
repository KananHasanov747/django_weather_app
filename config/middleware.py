import os
import json

from django.http import Http404
from servestatic.middleware import ServeStaticMiddleware

from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils.deprecation import MiddlewareMixin

from .logging_config import django_logger


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log request info
        django_logger.info(
            f"Request: {request.method} {request.path}",
            # FIX: extra is not showing
            extra={
                "user": request.user if request.user.is_authenticated else "Anonymous"
            },
        )

        response = self.get_response(request)

        # Log response info
        django_logger.info(f"Response: {response.status_code} for {request.path}")

        return response


class RestrictDirectAccessMiddleware(MiddlewareMixin):
    # List of URLs to restrict
    RESTRICTED_URLS = ["/admin/", "/api/"]
    RESTRICTED_PATTERNS = ["api:city", "api:weather"]

    def process_request(self, request):
        # Check if the requested path is in the restricted list
        if (
            request.path in self.RESTRICTED_URLS
            or request.resolver_match in self.RESTRICTED_PATTERNS
        ):
            # Get the referer header (where the request came from)
            referer = request.META.get("HTTP_REFERER")
            # Check if referer exists and starts with your domain
            if referer and (
                referer.startswith(f"http://{settings.ALLOWED_HOSTS[0]}")
                or referer.startswith(f"https://{settings.ALLOWED_HOSTS[0]}")
            ):
                # Internal request from your site, allow it
                return None
            else:
                # Direct or external request, check permissions
                if not request.user.is_staff or not request.user.is_superuser:
                    raise Http404()

        # Not a restricted URL, proceed normally
        return None


class CustomServeStaticMiddleware(ServeStaticMiddleware):
    """
    Custom version of ServeStaticMiddleware
    for serving '.png', '.jpg', and '.jpeg' as '.webp'
    with a fallback
    """

    IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Load the manifest to map original names to hashed names
        self.manifest = self.load_manifest()

    def load_manifest(self):
        if staticfiles_storage.manifest_name and staticfiles_storage.exists(
            staticfiles_storage.manifest_name
        ):
            with staticfiles_storage.open(staticfiles_storage.manifest_name) as f:
                return json.load(f)
        return {"paths": {}}

    async def __call__(self, request):
        accept = request.headers.get("Accept", "")
        client_accepts_webp = "image/webp" in accept
        path_info = request.path_info.replace("/static/", "")

        # Attempt to find the WebP version using the original filename
        original_name = self.get_original_name(path_info)
        if client_accepts_webp and original_name:
            webp_original_name = os.path.splitext(original_name)[0] + ".webp"
            webp_hashed_name = self.manifest["paths"].get(webp_original_name)
            if webp_hashed_name:
                # Serve the hashed WebP file
                lookup_key = f"{self.static_prefix}{webp_hashed_name}"
                static_file = self.files.get(lookup_key)
                if static_file:
                    return await self.aserve(static_file, request)

        # Fallback to original logic
        return await super().__call__(request)

    def get_original_name(self, hashed_path):
        # Reverse lookup to find the original filename from the hashed path
        for original, hashed in self.manifest.get("paths", {}).items():
            if hashed == hashed_path:
                return original
        return None
