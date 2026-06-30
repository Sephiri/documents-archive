from django.contrib import admin

from archive.models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ["id", "doc_type", "convent_type", "convent_number", "version_date", "is_extraordinary"]
    list_filter = ["doc_type", "convent_type", "is_extraordinary"]
    ordering = ["-version_date", "-convent_number"]
