
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin[User]):
    list_display = (
        "email",
        "first_name",
        "last_name",
        "global_role",
        "is_staff",
        "is_superuser",
        "is_active",
    )
    list_filter = ("global_role", "is_staff", "is_superuser", "is_active")
    ordering = ("email",)
    search_fields = ("email", "first_name", "last_name")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Información personal"),
            {"fields": ("first_name", "last_name", "profile_image")},
        ),
        (
            _("Permisos y roles"),
            {
                "fields": (
                    "global_role",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_email_verified",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Fechas importantes"), {"fields": ("last_login", "date_joined")}),
    )
