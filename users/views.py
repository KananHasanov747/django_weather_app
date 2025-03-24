from asgiref.sync import sync_to_async
from django_ratelimit.core import is_ratelimited
from django_ratelimit.exceptions import Ratelimited

from django.http import (
    HttpResponse,
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
)
from django.contrib.auth import alogin, aauthenticate, alogout
from django.shortcuts import render, redirect, reverse
from loguru import logger

from users.forms import LoginForm, RegisterForm


# path("/accounts/login/", views.login_view, name="login")
async def login_view(
    request,  # ASGIRequest
) -> None | HttpResponse | HttpResponseRedirect | HttpResponsePermanentRedirect:
    logger.bind(view="login_view")

    context = {"auth_action": "login", "switch_action": "signup"}
    template_name = "components/auth.html" if request.htmx else "index.html"

    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if await sync_to_async(form.is_valid)():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = await aauthenticate(request, username=username, password=password)
            if user:
                await alogin(request, user)
                logger.success(f"User '{username}' successfully logged in")
                return redirect(reverse("client:index"))
            else:
                logger.warning(f"Failed login attempt for '{username}'")
        else:
            logger.error("Login form invalid")
            return render(request, template_name, {"form": form, **context})

    else:
        logger.info("GET request to render the login form")
        form = LoginForm()

        return render(request, template_name, {"form": form, **context})


# path("/accounts/signup/", views.signup_view, name="signup")
async def signup_view(
    request,  # ASGIRequest
) -> None | HttpResponse | HttpResponseRedirect | HttpResponsePermanentRedirect:
    logger.bind(view="signup_view")

    # Check if the request is rate-limited
    if await sync_to_async(is_ratelimited)(
        request,
        fn=signup_view,
        key="ip",  # Rate limit based on IP address
        rate="1/30s",  # 1 request per 30 seconds
        method="POST",  # Apply to POST requests
        increment=True,  # Increment the counter
    ):
        logger.warning("Rate-limited signup attempt from IP")
        # Handle rate limit exceeded
        raise Ratelimited()

    context = {"auth_action": "signup", "switch_action": "login"}
    template_name = "components/auth.html" if request.htmx else "index.html"

    if request.method == "POST":
        form = RegisterForm(data=request.POST)
        if await sync_to_async(form.is_valid)():
            await sync_to_async(form.save)()
            logger.success(f"New user registered: {form.cleaned_data['username']}")
            return redirect(reverse("users:login"))
        else:
            logger.error("Signup form invalid")
            return render(request, template_name, {"form": form, **context})

    else:
        logger.info("GET request to render the signup form")
        form = RegisterForm()

        return render(request, template_name, {"form": form, **context})


# path("/accounts/logout/", views.logout_view, name="logout")
async def logout_view(
    request,  # ASGIRequest
) -> HttpResponseRedirect | HttpResponsePermanentRedirect:
    logger.bind(view="logout_view")

    await alogout(request)
    logger.success("User logged out, redirecting to index page")

    return redirect(reverse("client:index"))
