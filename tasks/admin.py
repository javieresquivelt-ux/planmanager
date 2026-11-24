from django.contrib import admin

from .models import Attachment, Comment, Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin[Task]):
    list_display = (
        "title",
        "project",
        "assignees_display",
        "status",
        "priority",
        "due_date",
    )
    list_filter = ("status", "priority")

    @admin.display(description="Asignados")
    def assignees_display(self, obj: Task) -> str:
        return ", ".join(u.email for u in obj.assignees.all())


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin[Comment]):
    list_display = ("task", "author", "created_at")


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin[Attachment]):
    list_display = ("task", "uploaded_by", "file", "created_at")
