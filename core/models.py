from django.db import models


class SiteConfig(models.Model):
    """Configuración global del sitio. Acceso vía SiteConfig.load()."""

    site_name = models.CharField(max_length=200, default="PlanManager")
    support_email = models.EmailField(default="soporte@ejemplo.com")

    class Meta:
        verbose_name = "Configuración del sitio"
        verbose_name_plural = "Configuración del sitio"

    def __str__(self) -> str:
        return self.site_name

    @classmethod
    def load(cls) -> SiteConfig:
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
