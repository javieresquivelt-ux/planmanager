from io import BytesIO

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from django.utils.translation import gettext_lazy as _
from PIL import Image

from .models import User

_AVATAR_SCALE = 1 / 3


def _resize_avatar(uploaded: UploadedFile[bytes]) -> InMemoryUploadedFile:
    original = Image.open(uploaded)
    width, height = original.size
    resized = original.resize(
        (max(1, int(width * _AVATAR_SCALE)), max(1, int(height * _AVATAR_SCALE))),
        Image.Resampling.LANCZOS,
    )
    buffer = BytesIO()
    fmt = original.format or "PNG"
    kwargs = {"quality": 85} if fmt == "JPEG" else {}
    resized.save(buffer, format=fmt, **kwargs)
    return InMemoryUploadedFile(
        buffer,
        None,
        uploaded.name,
        uploaded.content_type,
        buffer.getbuffer().nbytes,
        None,
    )


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
        fields = ("first_name", "last_name", "email", "profile_image")

    def save(self, commit: bool = True) -> User:
        user = super().save(commit=False)
        image = self.cleaned_data.get("profile_image")
        if image:
            user.profile_image = _resize_avatar(image)
        if commit:
            user.save()
        return user
