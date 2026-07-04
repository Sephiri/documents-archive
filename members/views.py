from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render

from .forms import MemberProfileForm
from .models import Member
from .services import get_member_directory


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

    members = get_member_directory(q=q, status=status)

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
