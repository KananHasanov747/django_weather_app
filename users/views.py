from asgiref.sync import sync_to_async

from django.core.handlers.asgi import ASGIRequest
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
)
from django.contrib.auth import alogin, alogout
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.forms import AuthenticationForm

from users.forms import RegisterForm


# path("/accounts/<str:action>/", views.auth_view, name="auth")
async def auth_view(
    request: ASGIRequest, action: str
) -> None | HttpResponse | HttpResponseRedirect | HttpResponsePermanentRedirect:
    if action not in ["login", "signup", "logout"]:
        return HttpResponseBadRequest("Invalid action")

    if request.method == "POST":
        if action == "login":
            form = AuthenticationForm(data=request.POST)
            if await sync_to_async(form.is_valid)():
                user = form.get_user()
                await alogin(request, user)
                return redirect(reverse("client:index"))
        elif action == "signup":
            form = RegisterForm(data=request.POST)
            if await sync_to_async(form.is_valid)():
                await sync_to_async(form.save)()
                return redirect(reverse("users:auth", kwargs={"action": "login"}))
    elif action == "logout":
        await alogout(request)
        return redirect(reverse("client:index"))
    else:
        form = AuthenticationForm() if action == "login" else RegisterForm()

        template_name = (
            f"components/auth/{action}.html" if request.htmx else "index.html"
        )
        return await sync_to_async(render)(
            request, template_name, {"form": form, "action": action}
        )
