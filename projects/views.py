from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from . import selectors, services
from .forms import MemberAddForm, ProjectForm
from .mixins import ProjectMemberRequiredMixin, ProjectOwnerRequiredMixin
from .models import Project, ProjectMembership

User = get_user_model()


class ProjectListView(LoginRequiredMixin, ListView):
    template_name = "projects/list.html"
    context_object_name = "projects"

    def get_queryset(self):
        return selectors.projects_for_user(self.request.user)


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/form.html"

    def form_valid(self, form):
        self.object = services.create_project(owner=self.request.user, **form.cleaned_data)
        return redirect(self.object.get_absolute_url())


class ProjectDetailView(ProjectMemberRequiredMixin, DetailView):
    model = Project
    template_name = "projects/detail.html"
    context_object_name = "project"
    pk_url_kwarg = "project_pk"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["memberships"] = self.object.memberships.select_related("user").all()
        ctx["member_form"] = MemberAddForm()
        ctx["role_choices"] = ProjectMembership.Role.choices
        ctx["user_role"] = self.get_role()
        return ctx


class ProjectUpdateView(ProjectOwnerRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/form.html"
    pk_url_kwarg = "project_pk"


class ProjectDeleteView(ProjectOwnerRequiredMixin, DeleteView):
    model = Project
    template_name = "projects/confirm_delete.html"
    success_url = reverse_lazy("projects:list")
    pk_url_kwarg = "project_pk"


class MemberAddView(ProjectOwnerRequiredMixin, View):
    def post(self, request, project_pk):
        project = self.get_project()
        form = MemberAddForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            role = form.cleaned_data["role"]
            try:
                services.add_member(project, email, role)
            except User.DoesNotExist:
                messages.error(request, "No existe un usuario con ese email.")
        return redirect("projects:detail", project_pk=project.pk)


class MemberRoleView(ProjectOwnerRequiredMixin, View):
    def post(self, request, project_pk, membership_pk):
        project = self.get_project()
        membership = get_object_or_404(
            ProjectMembership, pk=membership_pk, project=project
        )
        role = request.POST.get("role")
        if role in ProjectMembership.Role.values:
            services.set_membership_role(membership, role)
        return redirect("projects:detail", project_pk=project.pk)


class MemberRemoveView(ProjectOwnerRequiredMixin, View):
    def post(self, request, project_pk, membership_pk):
        project = self.get_project()
        membership = get_object_or_404(
            ProjectMembership, pk=membership_pk, project=project
        )
        if membership.role == ProjectMembership.Role.OWNER:
            messages.error(request, "No puedes eliminar al propietario.")
        else:
            membership.delete()
        return redirect("projects:detail", project_pk=project.pk)
