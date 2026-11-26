from typing import Any

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager["User"]):
    use_in_migrations = True

    def _create_user(
        self, email: str, password: str | None, **extra_fields: Any
    ) -> User:
        if not email:
            raise ValueError("El email es obligatorio.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(
        self, email: str, password: str | None = None, **extra_fields: Any
    ) -> User:
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(
        self, email: str, password: str | None = None, **extra_fields: Any
    ) -> User:
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    class GlobalRole(models.TextChoices):
        JP = "JP", _("Jefe de Proyecto")
        MEMBER = "MEMBER", _("Miembro")

    username = None  # type: ignore[assignment]
    email = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)
    profile_image = models.ImageField(_("foto de perfil"), upload_to="avatars/", blank=True)
    global_role = models.CharField(
        _("rol global"),
        max_length=20,
        choices=GlobalRole.choices,
        default=GlobalRole.JP,
        db_index=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []  # type: ignore[misc]

    objects = UserManager()  # type: ignore[assignment, misc]

    @property
    def can_create_projects(self) -> bool:
        return bool(self.is_superuser or self.global_role == self.GlobalRole.JP)

    @property
    def is_jp(self) -> bool:
        return self.global_role == self.GlobalRole.JP

    def __str__(self) -> str:
        return self.email
