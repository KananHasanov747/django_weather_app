from asgiref.sync import sync_to_async
from django.contrib.auth import alogin, alogout
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.forms import AuthenticationForm


# path("/accounts/login", views.login_view, name="login")
async def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if await sync_to_async(form.is_valid)():
            user = await sync_to_async(form.get_user)()
            await alogin(request, user)
            return redirect(reverse("client:index"))

    else:
        form = await sync_to_async(AuthenticationForm)()

        template_name = "components/auth.html" if request.htmx else "index.html"

        return render(request, template_name, {"form": form})


# path("/accounts/logout", views.logout_view, name="logout")
async def logout_view(request):
    await alogout(request)
    return redirect(reverse("client:index"))
