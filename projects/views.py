import csv
from typing import Any, cast

from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from users.models import User

from . import selectors, services
from .forms import MemberAddForm, ProjectForm
from .mixins import ProjectMemberRequiredMixin, ProjectOwnerRequiredMixin
from .models import Project, ProjectMembership


class ProjectListView(LoginRequiredMixin, ListView[Project]):
    template_name = "projects/list.html"
    context_object_name = "projects"

    def get_queryset(self) -> QuerySet[Project]:
        return selectors.projects_for_user(cast(User, self.request.user))


class ProjectPortfolioCSVView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest) -> HttpResponse:
        user = cast(User, request.user)
        projects = selectors.projects_for_user(user).prefetch_related(
            "tasks__assignees"
        )

        filename = (
            f"portafolio_proyectos_{timezone.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        # UTF-8 BOM para soporte nativo en Excel
        response.write("\ufeff")

        writer = csv.writer(response)
        writer.writerow([
            "Nombre-Proyecto",
            "Tareas",
            "Estado",
            "Prioridad",
            "Fecha Creación",
            "Fecha Límite",
            "Asignado A",
        ])

        for project in projects:
            tasks = project.tasks.all()
            if not tasks.exists():
                writer.writerow([
                    project.name,
                    "Sin tareas",
                    "-",
                    "-",
                    project.created_at.strftime("%Y-%m-%d"),
                    "-",
                    "-",
                ])
            else:
                for task in tasks:
                    assignees = (
                        ", ".join(
                            a.get_full_name() or a.email
                            for a in task.assignees.all()
                        )
                        or "Sin asignar"
                    )
                    writer.writerow([
                        project.name,
                        task.title,
                        task.get_status_display(),
                        task.get_priority_display(),
                        task.created_at.strftime("%Y-%m-%d"),
                        (
                            task.due_date.strftime("%Y-%m-%d")
                            if task.due_date
                            else "-"
                        ),
                        assignees,
                    ])

        return response


class ProjectCreateView(LoginRequiredMixin, CreateView[Project]):
    model = Project
    form_class = ProjectForm
    template_name = "projects/form.html"

    def dispatch(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse:
        if not request.user.is_authenticated:
            return cast(HttpResponse, self.handle_no_permission())
        user = request.user
        if not user.can_create_projects:
            raise PermissionDenied("No tienes permisos para crear proyectos.")
        return cast(HttpResponse, super().dispatch(request, *args, **kwargs))

    def form_valid(self, form: forms.ModelForm[Project]) -> HttpResponse:
        self.object = services.create_project(
            creator=cast(User, self.request.user), **form.cleaned_data
        )
        return redirect(self.object.get_absolute_url())


class ProjectDetailView(ProjectMemberRequiredMixin, DetailView[Project]):
    model = Project
    template_name = "projects/detail.html"
    context_object_name = "project"
    pk_url_kwarg = "project_pk"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        ctx["memberships"] = self.object.memberships.select_related("user").all()
        ctx["member_form"] = MemberAddForm()
        ctx["role_choices"] = ProjectMembership.Role.choices
        ctx["user_role"] = self.get_role()
        return ctx


class ProjectUpdateView(ProjectOwnerRequiredMixin, UpdateView[Project]):
    model = Project
    form_class = ProjectForm
    template_name = "projects/form.html"
    pk_url_kwarg = "project_pk"


class ProjectDeleteView(ProjectOwnerRequiredMixin, DeleteView[Project]):
    model = Project
    template_name = "projects/confirm_delete.html"
    success_url = reverse_lazy("projects:list")
    pk_url_kwarg = "project_pk"


class MemberAddView(ProjectOwnerRequiredMixin, View):
    def post(self, request: HttpRequest, project_pk: int) -> HttpResponse:
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
    def post(
        self, request: HttpRequest, project_pk: int, membership_pk: int
    ) -> HttpResponse:
        project = self.get_project()
        membership = get_object_or_404(
            ProjectMembership, pk=membership_pk, project=project
        )
        role = request.POST.get("role")
        if role in ProjectMembership.Role.values:
            services.set_membership_role(membership, role)
        return redirect("projects:detail", project_pk=project.pk)


class MemberRemoveView(ProjectOwnerRequiredMixin, View):
    def post(
        self, request: HttpRequest, project_pk: int, membership_pk: int
    ) -> HttpResponse:
        project = self.get_project()
        membership = get_object_or_404(
            ProjectMembership, pk=membership_pk, project=project
        )
        if membership.role == ProjectMembership.Role.OWNER:
            messages.error(request, "No puedes eliminar al propietario.")
        else:
            membership.delete()
        return redirect("projects:detail", project_pk=project.pk)
