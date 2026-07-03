from pathlib import Path

from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import FileResponse, Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from django.views.decorators.clickjacking import xframe_options_sameorigin

from .models import Document
from .permissions import can_view_document


@login_required
def document_list(request):
    member = request.user.member

    documents = Document.objects.all().order_by("-version_date")

    for document in documents:
        document.can_view = can_view_document(member, document)

    return render(
        request,
        "documents/document_list.html",
        {"documents": documents},
    )

@login_required
@xframe_options_sameorigin
def document_file(request, document_id):
    member = request.user.member
    document = get_object_or_404(Document, pk=document_id)

    if not can_view_document(member, document):
        return HttpResponseForbidden("Kein Zugriff auf dieses Dokument.")

    if not document.archive_path:
        raise Http404("Keine Datei hinterlegt.")

    archive_root = Path(settings.ARCHIVE_ROOT).resolve()
    file_path = (archive_root / document.archive_path).resolve()

    if not str(file_path).startswith(str(archive_root)):
        return HttpResponseForbidden("Ungültiger Dateipfad.")

    if not file_path.exists():
        raise Http404("Datei nicht gefunden.")

    response = FileResponse(
        open(file_path, "rb"),
        content_type="application/pdf",
    )
    response["Content-Disposition"] = f'inline; filename="{file_path.name}"'
    return response

@login_required
def document_detail(request, document_id):
    member = request.user.member
    document = get_object_or_404(Document, pk=document_id)

    if not can_view_document(member, document):
        return HttpResponseForbidden("Kein Zugriff auf dieses Dokument.")

    return render(
        request,
        "documents/document_detail.html",
        {"document": document},
    )