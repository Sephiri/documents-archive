from pathlib import Path

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import FileResponse, Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from django.views.decorators.clickjacking import xframe_options_sameorigin

from .models import Document
from .permissions import can_view_document


@login_required
def document_list(request):
    member = request.user.member

    q = request.GET.get("q", "").strip()
    doc_type = request.GET.get("doc_type", "").strip()
    convent_type = request.GET.get("convent_type", "").strip()
    sort = request.GET.get("sort", "-version_date")

    documents = Document.objects.all()

    if q:
        documents = documents.filter(Q(doc_type__icontains=q) | Q(convent_type__icontains=q) | Q(archive_path__icontains=q))

    if doc_type:
        documents = documents.filter(doc_type=doc_type)

    if convent_type:
        documents = documents.filter(convent_type=convent_type)

    allowed_sorts = {
        "-version_date",
        "version_date",
        "-uploaded_at",
        "uploaded_at",
        "doc_type",
        "convent_type",
    }

    if sort not in allowed_sorts:
        sort = "-version_date"

    documents = documents.order_by(sort)

    for document in documents:
        document.can_view = can_view_document(member, document)

    doc_types = (
        Document.objects.exclude(doc_type__isnull=True).exclude(doc_type="").values_list("doc_type", flat=True).distinct().order_by("doc_type")
    )

    convent_types = (
        Document.objects.exclude(convent_type__isnull=True)
        .exclude(convent_type="")
        .values_list("convent_type", flat=True)
        .distinct()
        .order_by("convent_type")
    )

    return render(
        request,
        "documents/document_list.html",
        {
            "documents": documents,
            "doc_types": doc_types,
            "convent_types": convent_types,
            "q": q,
            "selected_doc_type": doc_type,
            "selected_convent_type": convent_type,
            "selected_sort": sort,
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
