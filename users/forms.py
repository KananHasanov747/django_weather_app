from django import forms
from .models import User


# TODO: response returns 'None'; fix RegisterForm
class RegisterForm(forms.ModelForm):
    username = forms.CharField(
        max_length=32,
        required=True,
        widget=forms.TextInput(),
    )
    password = forms.CharField(
        min_length=3,
        required=True,
        widget=forms.PasswordInput(),
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
