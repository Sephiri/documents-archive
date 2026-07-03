from django.contrib import admin
from .models import Member, Office, OfficeAssignment


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "email",
        "phone", 
        "address_line",
        "postal_code",
        "city",
        "study_program",
        "status",
        "activity_status",
        "joined_at",
        "joined_semester", 
        "joined_semester_year",
        "is_current_member",
        "user",
    )
    list_filter = ("status", "activity_status", "is_current_member")
    search_fields = ("first_name", "middle_names", "last_name", "email")


@admin.register(Office)
class OfficeAdmin(admin.ModelAdmin):
    list_display = ("name", "is_charge", "grants_board_rights")
    search_fields = ("name",)


@admin.register(OfficeAssignment)
class OfficeAssignmentAdmin(admin.ModelAdmin):
    list_display = ("member", "office", "start_date", "end_date")
    list_filter = ("office",)
    search_fields = (
        "member__first_name",
        "member__last_name",
        "office__name",
    )