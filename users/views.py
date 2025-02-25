from asgiref.sync import sync_to_async
from django.contrib.auth import alogin, alogout
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.forms import AuthenticationForm

from users.forms import RegisterForm


# path("/accounts/login", views.login_view, name="login")
async def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if await sync_to_async(form.is_valid)():
            user = form.get_user()
            await alogin(request, user)
            return redirect(reverse("client:index"))

    else:
        form = AuthenticationForm()

        template_name = "components/auth/login.html" if request.htmx else "index.html"

        return render(request, template_name, {"form": form})


async def signup_view(request):
    if request.method == "POST":
        form = RegisterForm(data=request.POST)
        if await sync_to_async(form.is_valid)():
            await sync_to_async(form.save)()
            return redirect(reverse("users:login"))

    else:
        form = RegisterForm()

        template_name = "components/auth/signup.html" if request.htmx else "index.html"

        return render(request, template_name, {"form": form})


# path("/accounts/logout", views.logout_view, name="logout")
async def logout_view(request):
    await alogout(request)
    return redirect(reverse("client:index"))
