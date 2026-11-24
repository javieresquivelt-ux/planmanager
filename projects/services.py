from django.contrib.auth import get_user_model

from .models import Project, ProjectMembership

User = get_user_model()


def create_project(*, owner, name, description=""):
    project = Project.objects.create(owner=owner, name=name, description=description)
    ProjectMembership.objects.create(
        project=project, user=owner, role=ProjectMembership.Role.OWNER
    )
    return project


def add_member(project, email, role):
    user = User.objects.get(email=email)
    membership, created = ProjectMembership.objects.get_or_create(
        project=project, user=user, defaults={"role": role}
    )
    if not created:
        membership.role = role
        membership.save(update_fields=["role"])
    return membership


def set_membership_role(membership, role):
    membership.role = role
    membership.save(update_fields=["role"])
    return membership
