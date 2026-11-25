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
    Image.new("RGB", (90, 60), color=(80, 90, 200)).save(buf, format="PNG")
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

        with user.profile_image.open("rb") as f:
            img = Image.open(f)
            assert img.size == (30, 20)


@pytest.mark.django_db
def test_user_global_role_and_can_create_projects():
    member = User.objects.create_user(email="member@example.com", password="pwd")
    assert member.global_role == User.GlobalRole.MEMBER
    assert member.can_create_projects is False
    assert member.is_jp is False

    jp = User.objects.create_user(
        email="jp@example.com", password="pwd", global_role=User.GlobalRole.JP
    )
    assert jp.can_create_projects is True
    assert jp.is_jp is True

    admin = User.objects.create_superuser(email="admin@example.com", password="pwd")
    assert admin.can_create_projects is True


@pytest.mark.django_db
def test_user_management_view_permissions(client):
    member = User.objects.create_user(email="member@example.com", password="pwd")
    jp = User.objects.create_user(
        email="jp@example.com", password="pwd", global_role=User.GlobalRole.JP
    )
    superadmin = User.objects.create_superuser(
        email="root@example.com", password="pwd"
    )

    # Anónimo redirige a login
    resp = client.get(reverse("users:manage"))
    assert resp.status_code == 302

    # Member obtiene 403
    client.force_login(member)
    resp = client.get(reverse("users:manage"))
    assert resp.status_code == 403

    # JP obtiene 403
    client.force_login(jp)
    resp = client.get(reverse("users:manage"))
    assert resp.status_code == 403

    # Superadmin obtiene 200
    client.force_login(superadmin)
    resp = client.get(reverse("users:manage"))
    assert resp.status_code == 200
    assert b"member@example.com" in resp.content
    assert b"jp@example.com" in resp.content


@pytest.mark.django_db
def test_user_role_update_view_htmx(client):
    member = User.objects.create_user(email="collab@example.com", password="pwd")
    superadmin = User.objects.create_superuser(
        email="root@example.com", password="pwd"
    )

    client.force_login(superadmin)
    resp = client.post(
        reverse("users:update_role", kwargs={"user_pk": member.pk}),
        {"role": "JP"},
        HTTP_HX_REQUEST="true",
    )
    assert resp.status_code == 200
    member.refresh_from_db()
    assert member.global_role == User.GlobalRole.JP
    assert member.can_create_projects is True
    assert b"Jefe de Proyecto (JP)" in resp.content
