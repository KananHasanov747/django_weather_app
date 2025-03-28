from django import forms
from django.contrib.auth.forms import UsernameField

from .models import User

form_class = "py-[14px] px-2 rounded-[.6rem] leading-[18px] outline-none bg-light-gray text-[13px] text-light-white text-light-text placeholder:text-light-white"


class LoginForm(forms.Form):
    username = UsernameField(
        label="",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": form_class,
                "placeholder": "Username",
                "autocapitalize": "none",
                "autofocus": True,
            }
        ),
    )
    password = forms.CharField(
        label="",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": form_class,
                "placeholder": "Password",
                "max_length": 150,
                "autocomplete": "current-password",
            }
        ),
    )

    class Meta:
        model = User
        fields = ["username", "password"]


# TODO: add dynamic error
class RegisterForm(forms.ModelForm):
    username = forms.CharField(
        max_length=32,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": form_class,
                "placeholder": "Username",
                "autocapitalize": "none",
                "autofocus": True,
            }
        ),
    )
    password = forms.CharField(
        min_length=3,
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "class": form_class,
                "placeholder": "Password",
                "max_length": 150,
                "autocomplete": "current-password",
            }
        ),
    )

    class Meta:
        model = User
        fields = ["username", "password"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
