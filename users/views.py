from asgiref.sync import sync_to_async

from django.core.handlers.asgi import ASGIRequest
from django.http import (
    HttpResponse,
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
)
from django.contrib.auth import alogin, alogout
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.forms import AuthenticationForm

from users.forms import RegisterForm


# path("/accounts/login/", views.login_view, name="login")
async def login_view(
    request: ASGIRequest,
) -> None | HttpResponse | HttpResponseRedirect | HttpResponsePermanentRedirect:
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if await sync_to_async(form.is_valid)():
            user = form.get_user()
            await alogin(request, user)
            return redirect(reverse("client:index"))

    else:
        form = AuthenticationForm()

        template_name = "components/auth/login.html" if request.htmx else "index.html"

        return render(request, template_name, {"form": form, "action": "login"})


# path("/accounts/signup/", views.signup_view, name="signup")
async def signup_view(
    request: ASGIRequest,
) -> None | HttpResponse | HttpResponseRedirect | HttpResponsePermanentRedirect:
    if request.method == "POST":
        form = RegisterForm(data=request.POST)
        if await sync_to_async(form.is_valid)():
            await sync_to_async(form.save)()
            return redirect(reverse("users:login"))

    else:
        form = RegisterForm()

        template_name = "components/auth/signup.html" if request.htmx else "index.html"

        return render(request, template_name, {"form": form, "action": "signup"})


# path("/accounts/logout/", views.logout_view, name="logout")
async def logout_view(
    request: ASGIRequest,
) -> HttpResponseRedirect | HttpResponsePermanentRedirect:
    await alogout(request)
    return redirect(reverse("client:index"))
