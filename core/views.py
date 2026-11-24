from typing import Any, cast

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic import TemplateView

from users.models import User

from . import selectors


def home(request: HttpRequest) -> HttpResponseRedirect:
    if request.user.is_authenticated:
        return redirect("dashboard")
    return redirect("users:login")


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "core/dashboard.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        ctx.update(selectors.dashboard_metrics(cast(User, self.request.user)))
        return ctx
