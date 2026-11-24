from typing import Any

from django import template

from users.models import User

register = template.Library()


@register.inclusion_tag("core/partials/avatar.html")
def avatar(user: User, size: str = "h-6 w-6", text: str = "text-xs") -> dict[str, Any]:
    return {"user": user, "size": size, "text": text}
