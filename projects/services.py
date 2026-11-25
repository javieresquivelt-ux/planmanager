from users.models import User

from .models import Project, ProjectMembership


def create_project(
    *,
    creator: User | None = None,
    owner: User | None = None,
    name: str,
    description: str = "",
) -> Project:
    actual_creator = creator or owner
    if actual_creator is None:
        raise ValueError("Se requiere el usuario creador del proyecto.")

    if actual_creator.is_superuser:
        actual_owner = actual_creator
        creator_role = ProjectMembership.Role.OWNER
    else:
        # Superadministrador institucional por defecto del sistema
        superadmin = (
            User.objects.filter(is_superuser=True, is_active=True)
            .order_by("id")
            .first()
        )
        actual_owner = superadmin if superadmin else actual_creator
        creator_role = ProjectMembership.Role.MANAGER

    project = Project.objects.create(
        owner=actual_owner, name=name, description=description
    )
    ProjectMembership.objects.get_or_create(
        project=project,
        user=actual_owner,
        defaults={"role": ProjectMembership.Role.OWNER},
    )

    if actual_creator != actual_owner:
        ProjectMembership.objects.create(
            project=project, user=actual_creator, role=creator_role
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
