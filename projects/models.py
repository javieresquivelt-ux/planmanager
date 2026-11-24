from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from users.models import User


class Project(models.Model):
    name = models.CharField(_("nombre"), max_length=200)
    description = models.TextField(_("descripción"), blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_projects",
        verbose_name=_("propietario"),
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="ProjectMembership",
        related_name="projects",
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("projects:detail", kwargs={"project_pk": self.pk})


class ProjectMembership(models.Model):
    class Role(models.TextChoices):
        OWNER = "OWNER", _("Propietario")
        MANAGER = "MANAGER", _("Gestor")
        MEMBER = "MEMBER", _("Miembro")
        VIEWER = "VIEWER", _("Invitado")

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="memberships"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memberships"
    )
    role = models.CharField(
        _("rol"),
        max_length=20,
        choices=Role.choices,
        default=Role.MEMBER,
        db_index=True,
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("project", "user")
        indexes = [models.Index(fields=["project", "role"])]
        verbose_name = _("membresía")
        verbose_name_plural = _("membresías")

    def __str__(self) -> str:
        return f"{self.user} — {self.project} ({self.get_role_display()})"

    @classmethod
    def get_role(cls, user: User, project: Project) -> str | None:
        """Rol del usuario en el proyecto, o ``None`` si no es miembro."""
        membership = (
            cls.objects.filter(user=user, project=project).only("role").first()
        )
        return membership.role if membership else None
