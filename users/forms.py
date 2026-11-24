from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.translation import gettext_lazy as _

from .models import User


class UserRegistrationForm(UserCreationForm[User]):
    """Registro por email. La contraseña se hashea vía UserCreationForm."""

    class Meta:
        model = User
        fields = ("email",)


class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={"autofocus": True}),
    )


class UserProfileForm(forms.ModelForm[User]):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")
