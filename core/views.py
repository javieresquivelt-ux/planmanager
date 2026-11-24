from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import TemplateView

from . import selectors


def home(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return redirect("users:login")


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "core/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(selectors.dashboard_metrics(self.request.user))
        return ctx
