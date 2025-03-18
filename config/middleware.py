from django.http import Http404
from loguru import logger
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


class XForwardedForMiddleware:
    """Deals with empty REMOTE_ADDR"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Modify the request as necessary
        if "HTTP_X_FORWARDED_FOR" in request.META:
            request.META["HTTP_X_PROXY_REMOTE_ADDR"] = request.META.get("REMOTE_ADDR")
            parts = request.META["HTTP_X_FORWARDED_FOR"].split(",", 1)
            request.META["REMOTE_ADDR"] = parts[0]

        # Call the next middleware or view
        response = self.get_response(request)
        return response


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log request info
        logger.info(
            f"Request: {request.method} {request.path}",
            # FIX: extra is not showing
            extra={
                "user": request.user if request.user.is_authenticated else "Anonymous"
            },
        )

        response = self.get_response(request)

        # Log response info
        logger.info(f"Response: {response.status_code} for {request.path}")

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
