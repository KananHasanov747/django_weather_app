import re
from django.http import Http404
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


class RestrictDirectAccessMiddleware(MiddlewareMixin):
    # List of URLs to restrict
    RESTRICTED_URLS = ["/admin/", "/api/"]
    RESTRICTED_PATTERNS = ["api:city", "api:weather"]

    def process_request(self, request):
        # Check if the requested path is in the restricted list
        if (
            any([request.path.startswith(_) for _ in self.RESTRICTED_URLS])
            or request.resolver_match in self.RESTRICTED_PATTERNS
        ):
            # Get the referer header (where the request came from)
            referer = request.META.get("HTTP_REFERER")
            # Check if referer exists and starts with your domain
            if referer and (
                any(
                    [
                        re.match(rf"^(http|https)://{re.escape(host)}", referer)
                        for host in settings.ALLOWED_HOSTS
                    ]
                )
            ):
                # Internal request from your site, allow it
                return None
            else:
                # Direct or external request, check permissions
                if not request.user.is_staff or not request.user.is_superuser:
                    raise Http404()

        # Not a restricted URL, proceed normally
        return None
