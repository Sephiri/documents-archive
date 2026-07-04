from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseForbidden, JsonResponse

from .serializers import serialize_document
from .services import get_filtered_documents


@login_required
def document_list_api(request):
    try:
        member = request.user.member
    except ObjectDoesNotExist:
        return HttpResponseForbidden("Kein Mitgliederprofil verknüpft.")

    if not member.is_current_member:
        return HttpResponseForbidden("Kein Zugriff.")

    q = request.GET.get("q", "").strip()
    doc_type = request.GET.get("doc_type", "").strip()
    convent_type = request.GET.get("convent_type", "").strip()
    sort = request.GET.get("sort", "-version_date").strip()

    documents = get_filtered_documents(
        member=member,
        q=q,
        doc_type=doc_type,
        convent_type=convent_type,
        sort=sort,
    )

    return JsonResponse(
        {
            "documents": [serialize_document(document) for document in documents],
        }
    )
