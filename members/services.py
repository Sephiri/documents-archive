from django.db.models import Prefetch, Q

from .models import Member, OfficeAssignment


def get_member_directory(*, q="", status=""):
    current_office_assignments = OfficeAssignment.objects.filter(
        end_date__isnull=True,
    ).select_related("office")

    members = (
        Member.objects.filter(is_current_member=True)
        .prefetch_related(
            Prefetch(
                "office_assignments",
                queryset=current_office_assignments,
                to_attr="current_office_assignments",
            )
        )
        .order_by("last_name", "first_name")
    )

    if q:
        members = members.filter(
            Q(first_name__icontains=q)
            | Q(middle_names__icontains=q)
            | Q(last_name__icontains=q)
            | Q(email__icontains=q)
            | Q(study_program__icontains=q)
            | Q(profession__icontains=q)
        )

    if status:
        members = members.filter(status=status)

    return members
