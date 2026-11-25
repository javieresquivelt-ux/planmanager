from typing import cast

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView

from .forms import UserProfileForm, UserRegistrationForm
from .models import User


class RegisterView(CreateView[User]):
    model = User
    form_class = UserRegistrationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("users:login")


class ProfileView(LoginRequiredMixin, UpdateView[User]):
    model = User
    form_class = UserProfileForm
    template_name = "users/profile.html"
    success_url = reverse_lazy("users:profile")

    def get_object(self, queryset: QuerySet[User] | None = None) -> User:
        return cast(User, self.request.user)


class UserManagementView(LoginRequiredMixin, UserPassesTestMixin, ListView[User]):
    model = User
    template_name = "users/management.html"
    context_object_name = "users_list"

    def test_func(self) -> bool:
        return bool(self.request.user.is_superuser)

    def get_queryset(self) -> QuerySet[User]:
        return User.objects.all().order_by("id")


class UserRoleUpdateView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self) -> bool:
        return bool(self.request.user.is_superuser)

    def post(self, request: HttpRequest, user_pk: int) -> HttpResponse:
        target_user = get_object_or_404(User, pk=user_pk)
        new_role = request.POST.get("role")
        if new_role in User.GlobalRole.values:
            target_user.global_role = new_role
            target_user.save(update_fields=["global_role"])

        if request.headers.get("HX-Request"):
            return render(
                request,
                "users/partials/role_badge.html",
                {"u": target_user},
            )
        return redirect("users:manage")
