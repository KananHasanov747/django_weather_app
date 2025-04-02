from django.http import Http404
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from loguru import logger


class XForwardedForMiddleware:
    """Deals with prxoy requests"""

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
    # URLs and patterns to restrict
    RESTRICTED_URLS = ["/admin/", "/api/"]
    RESTRICTED_PATTERNS = ["api:city", "api:weather"]

    def process_request(self, request):
        # Check if the request targets a restricted URL or pattern
        resolver_match = getattr(request, "resolver_match", None)
        url_name = resolver_match.url_name if resolver_match else None
        is_restricted = any(
            request.path.startswith(url) for url in self.RESTRICTED_URLS
        ) or (url_name in self.RESTRICTED_PATTERNS)

        if is_restricted:
            # Log the access attempt
            logger.info(
                f"Access attempt to {request.path} from {request.META.get('REMOTE_ADDR')}"
            )

            # Check referer with stricter validation
            referer = request.META.get("HTTP_REFERER")
            if (
                referer
                and referer.startswith("https://")
                and any(
                    [
                        referer.endswith(
                            f"{host}/"
                        )  # http:// is redundant if SECURE_SSL_REDIRECT=True redirects HTTP to HTTPS
                        for host in settings.ALLOWED_HOSTS
                    ]
                )
            ):
                # Reuest coming from the enlisted host, proceed normally
                return None
            else:
                # Direct or external request, check permissions
                if not request.user.is_staff or not request.user.is_superuser:
                    logger.warning(f"Unauthorized access to {request.path} blocked")
                    raise Http404()

        # Not a restricted URL or pattern, proceed normally
        return None
