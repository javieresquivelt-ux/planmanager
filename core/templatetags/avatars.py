from typing import Any

from django import template

from users.models import User

register = template.Library()


@register.inclusion_tag("core/partials/avatar.html")
def avatar(user: User, size: str = "h-12 w-12", text: str = "text-sm") -> dict[str, Any]:
    return {"user": user, "size": size, "text": text}
