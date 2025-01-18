from dotenv import load_dotenv

from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin


from server.urls import urlpatterns

load_dotenv()


class RestrictDirectUrlAccessMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if (
            any([request.path.startswith(f"/{url.pattern}") for url in urlpatterns])
            and not (request.user.is_staff or request.user.is_superuser)
            and "application/json" not in request.headers.get("Accept")
        ):
            return HttpResponseForbidden("Access forbidden.")
        return None
