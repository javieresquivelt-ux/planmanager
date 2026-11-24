from io import BytesIO

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from PIL import Image

User = get_user_model()


@pytest.mark.django_db
def test_register_hashes_password_and_redirects(client):
    resp = client.post(
        reverse("users:register"),
        {
            "email": "test@planmanager.local",
            "password1": "Xyz_12345",
            "password2": "Xyz_12345",
        },
    )
    assert resp.status_code == 302
    assert resp.url == reverse("users:login")

    user = User.objects.get(email="test@planmanager.local")
    assert user.password != "Xyz_12345"
    assert user.check_password("Xyz_12345")


@pytest.mark.django_db
def test_login_and_logout(client):
    User.objects.create_user(email="test@planmanager.local", password="Xyz_12345")

    resp = client.post(
        reverse("users:login"),
        {"username": "test@planmanager.local", "password": "Xyz_12345"},
    )
    assert resp.status_code == 302
    assert resp.url == reverse("dashboard")
    assert client.session["_auth_user_id"]

    resp = client.post(reverse("users:logout"))
    assert resp.status_code == 302
    assert "_auth_user_id" not in client.session


@pytest.mark.django_db
def test_profile_requires_login(client):
    resp = client.get(reverse("users:profile"))
    assert resp.status_code == 302
    assert resp.url.startswith(reverse("users:login"))


@pytest.mark.django_db
def test_language_switch_to_english(client):
    resp = client.post(
        reverse("set_language"),
        {"language": "en", "next": reverse("users:login")},
    )
    assert resp.status_code == 302
    resp = client.get(reverse("users:login"))
    assert b"Log in" in resp.content
    assert b"Iniciar sesi" not in resp.content


@pytest.fixture
def image_file():
    buf = BytesIO()
    Image.new("RGB", (8, 8), color=(80, 90, 200)).save(buf, format="PNG")
    return SimpleUploadedFile(
        "avatar.png", buf.getvalue(), content_type="image/png"
    )


@pytest.mark.django_db
def test_profile_image_upload(client, image_file, tmp_path):
    user = User.objects.create_user(email="img@example.com", password="pass12345")
    client.force_login(user)
    with override_settings(MEDIA_ROOT=str(tmp_path)):
        resp = client.post(
            reverse("users:profile"),
            {
                "first_name": "Ana",
                "last_name": "Gómez",
                "email": user.email,
                "profile_image": image_file,
            },
        )
    assert resp.status_code == 302
    user.refresh_from_db()
    assert bool(user.profile_image)
    assert user.profile_image.name.startswith("avatars/")
