from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Prefetch, Q
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render

from .forms import MemberProfileForm
from .models import Member, OfficeAssignment


@login_required
def member_list(request):
    try:
        current_member = request.user.member
    except ObjectDoesNotExist:
        return HttpResponseForbidden("Kein Mitgliederprofil verknüpft.")

    if not current_member.is_current_member:
        return HttpResponseForbidden("Kein Zugriff auf das Mitgliederverzeichnis.")

    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()

    current_office_assignments = OfficeAssignment.objects.filter(
        end_date__isnull=True
    ).select_related("office")

    members = (
        Member.objects
        .filter(is_current_member=True)
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

    return render(
        request,
        "members/member_list.html",
        {
            "members": members,
            "q": q,
            "selected_status": status,
            "status_choices": Member.Status.choices,
        },
    )

@login_required
def member_profile(request):
    try:
        member = request.user.member
    except ObjectDoesNotExist:
        return HttpResponseForbidden("Kein Mitgliederprofil verknüpft.")

    if not member.is_current_member:
        return HttpResponseForbidden("Kein Zugriff.")

    if request.method == "POST":
        form = MemberProfileForm(request.POST, instance=member)

        if form.is_valid():
            form.save()
            messages.success(request, "Profil wurde gespeichert.")
            return redirect("members:member_profile")
    else:
        form = MemberProfileForm(instance=member)

    return render(
        request,
        "members/member_profile.html",
        {"form": form, "member": member},
    )