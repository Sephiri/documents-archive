from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseForbidden, JsonResponse

from .serializers import serialize_member
from .services import get_member_directory


@login_required
def member_list_api(request):
    try:
        current_member = request.user.member
    except ObjectDoesNotExist:
        return HttpResponseForbidden("Kein Mitgliederprofil verknüpft.")

    if not current_member.is_current_member:
        return HttpResponseForbidden("Kein Zugriff.")

    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()

    members = get_member_directory(q=q, status=status)

    return JsonResponse(
        {
            "members": [serialize_member(member) for member in members],
        }
    )
