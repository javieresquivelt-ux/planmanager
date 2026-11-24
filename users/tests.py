import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

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
