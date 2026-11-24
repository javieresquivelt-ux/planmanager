from typing import cast

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

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
