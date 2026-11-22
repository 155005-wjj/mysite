from django.contrib import admin
from app01.models import Knowledge


@admin.register(Knowledge)
class KnowledgeAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "content")
    search_fields = ("title", "content")
