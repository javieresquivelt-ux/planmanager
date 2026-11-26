from django import template

register = template.Library()

_STATUS_COLORS: dict[str, str] = {
    "TODO": "badge-slate",
    "IN_PROGRESS": "badge-blue",
    "REVIEW": "badge-amber",
    "DONE": "badge-green",
}

_PRIORITY_COLORS: dict[str, str] = {
    "LOW": "badge-slate",
    "MEDIUM": "badge-blue",
    "HIGH": "badge-amber",
    "URGENT": "badge-red",
}

_ROLE_COLORS: dict[str, str] = {
    "OWNER": "badge-amber",
    "MANAGER": "badge-blue",
    "MEMBER": "badge-slate",
    "VIEWER": "badge-slate",
}

_PROJECT_STATUS_COLORS: dict[str, str] = {
    "OPEN": "badge-green",
    "ON_HOLD": "badge-amber",
    "CLOSED": "badge-slate",
}


@register.filter
def status_badge(value: str) -> str:
    return f"badge {_STATUS_COLORS.get(value, 'badge-slate')}"


@register.filter
def project_status_badge(value: str) -> str:
    return f"badge {_PROJECT_STATUS_COLORS.get(value, 'badge-slate')}"


@register.filter
def priority_badge(value: str) -> str:
    return f"badge {_PRIORITY_COLORS.get(value, 'badge-slate')}"


@register.filter
def role_badge(value: str) -> str:
    return f"badge {_ROLE_COLORS.get(value, 'badge-slate')}"
