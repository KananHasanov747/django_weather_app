import os

from django.conf import settings
from django.http import HttpResponseNotFound
from django.utils.deprecation import MiddlewareMixin


from server.urls import urlpatterns


class RestrictDirectUrlAccessMiddleware(MiddlewareMixin):
    def process_request(self, request):

        if (
            not settings.DEBUG
            and (
                request.path.startswith(f'/{os.getenv("DJANGO_ADMIN_URL")}')
                or any(
                    [request.path.startswith(f"/{url.pattern}") for url in urlpatterns]
                )
            )
            and not (request.user.is_staff or request.user.is_superuser)
            and "application/json" not in request.headers.get("Accept")
        ):
            return HttpResponseNotFound()
        return None
