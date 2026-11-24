from django.http import HttpRequest

from core.models import SiteConfig


def site_config(request: HttpRequest) -> dict[str, SiteConfig]:
    return {"site": SiteConfig.load()}
