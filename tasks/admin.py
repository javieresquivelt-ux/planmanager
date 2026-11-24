from django.contrib import admin

from .models import Attachment, Comment, Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin[Task]):
    list_display = ("title", "project", "assignee", "status", "priority", "due_date")
    list_filter = ("status", "priority")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin[Comment]):
    list_display = ("task", "author", "created_at")


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin[Attachment]):
    list_display = ("task", "uploaded_by", "file", "created_at")
