from pathlib import Path

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from django.views.decorators.clickjacking import xframe_options_sameorigin

from .models import Document
from .permissions import can_view_document
from .services import get_document_filter_options, get_filtered_documents


@login_required
def document_list(request):
    member = request.user.member

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

    filter_options = get_document_filter_options()

    return render(
        request,
        "documents/document_list.html",
        {
            "documents": documents,
            "q": q,
            "selected_doc_type": doc_type,
            "selected_convent_type": convent_type,
            "selected_sort": sort,
            **filter_options,
        },
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
    response["X-Frame-Options"] = "SAMEORIGIN"
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


@login_required
def document_download(request, document_id):
    member = request.user.member
    document = get_object_or_404(Document, pk=document_id)

    if not can_view_document(member, document):
        return HttpResponseForbidden("Kein Zugriff auf dieses Dokument.")

    file_path = get_document_file_path(document)

    response = FileResponse(
        open(file_path, "rb"),
        content_type="application/pdf",
    )
    response["Content-Disposition"] = f'attachment; filename="{file_path.name}"'
    return response


def get_document_file_path(document):
    if not document.archive_path:
        raise Http404("Keine Datei hinterlegt.")

    archive_root = Path(settings.ARCHIVE_ROOT).resolve()
    file_path = (archive_root / document.archive_path).resolve()

    if not str(file_path).startswith(str(archive_root)):
        raise Http404("Ungültiger Dateipfad.")

    if not file_path.exists():
        raise Http404("Datei nicht gefunden.")

    return file_path
