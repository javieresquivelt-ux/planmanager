from users.models import User

from .models import Project, ProjectMembership


def create_project(*, owner: User, name: str, description: str = "") -> Project:
    project = Project.objects.create(owner=owner, name=name, description=description)
    ProjectMembership.objects.create(
        project=project, user=owner, role=ProjectMembership.Role.OWNER
    )
    return project


def add_member(project: Project, email: str, role: str) -> ProjectMembership:
    user = User.objects.get(email=email)
    membership, created = ProjectMembership.objects.get_or_create(
        project=project, user=user, defaults={"role": role}
    )
    if not created:
        membership.role = role
        membership.save(update_fields=["role"])
    return membership


def set_membership_role(membership: ProjectMembership, role: str) -> ProjectMembership:
    membership.role = role
    membership.save(update_fields=["role"])
    return membership
