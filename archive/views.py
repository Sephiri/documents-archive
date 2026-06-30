from __future__ import annotations

from dataclasses import asdict
import logging

from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import redirect, render
from django.utils.http import content_disposition_header

from archive.filters import get_semester_options, get_year_options
from archive.files import open_archive_file
from archive.labels import (
    PROTOCOL_TYPE_LABELS,
    STATUTE_TYPE_LABELS,
    DocumentData,
    build_document_meta_items,
    get_document_list_title,
    is_protocol_type,
    is_statute_type,
)
from archive.services import (
    DocumentFilters,
    get_cached_single_document_by_doc_type,
    get_document_by_id,
    get_filtered_documents,
)

logger = logging.getLogger(__name__)


def root_redirect(request):
    return redirect("intern-home")


def build_nav(current_path: str) -> list[dict]:
    return [
        {
            "title": "Protokolle",
            "group_active": current_path.startswith("/intern/protokolle"),
            "items": [
                {
                    "title": label,
                    "url": f"/intern/protokolle/{key}/",
                    "active": current_path == f"/intern/protokolle/{key}/",
                }
                for key, label in PROTOCOL_TYPE_LABELS.items()
            ],
        },
        {
            "title": "Statuten",
            "group_active": current_path.startswith("/intern/statuten"),
            "items": [
                {
                    "title": label,
                    "url": f"/intern/statuten/{key}/",
                    "active": current_path == f"/intern/statuten/{key}/",
                }
                for key, label in STATUTE_TYPE_LABELS.items()
            ],
        },
    ]


def base_context(request, main: str, current: str) -> dict:
    return {
        "nav_main": build_nav(request.path),
        "breadcrumb_main": main,
        "breadcrumb_current": current,
    }


def panel_context(document: DocumentData) -> dict:
    return {
        "document": document,
        "document_title": get_document_list_title(document),
        "document_meta_items": build_document_meta_items(document),
    }


def intern_home(request):
    context = base_context(request, "Intern", "Übersicht")
    return render(request, "archive/intern_home.html", context)


def protocol_view(request, protocol_type: str):
    if not is_protocol_type(protocol_type):
        raise Http404("Protokolltyp nicht gefunden")

    documents = get_filtered_documents(DocumentFilters(doc_type="protokoll", convent_type=protocol_type))
    selected_id = request.GET.get("selected")

    context = {
        **base_context(request, "Protokolle", PROTOCOL_TYPE_LABELS[protocol_type]),
        "title": PROTOCOL_TYPE_LABELS[protocol_type],
        "documents_json": [asdict(document) for document in documents],
        "document_count": len(documents),
        "selected_id": int(selected_id) if selected_id and selected_id.isdigit() else None,
        "semester_options_json": get_semester_options(documents),
        "year_options_json": get_year_options(documents),
    }

    return render(request, "archive/collection.html", context)


def statute_view(request, document_type: str):
    if not is_statute_type(document_type):
        raise Http404("Dokumenttyp nicht gefunden")

    document = get_cached_single_document_by_doc_type(document_type)
    context = {
        **base_context(request, "Statuten", STATUTE_TYPE_LABELS[document_type]),
        "empty_title": "Die Datei wurde nicht gefunden!",
        "empty_description": "Die Datei liegt nicht in der Datenbank. Lade das Dokument hoch.",
        "selected_panel": panel_context(document) if document else None,
    }

    return render(request, "archive/statute.html", context)


def file_view(request, document_id: int):
    document = get_document_by_id(document_id)

    if not document or not document.archive_path:
        return HttpResponse("Datei nicht gefunden", status=404, content_type="text/plain")

    try:
        file_handle = open_archive_file(document.archive_path)
    except (OSError, ValueError):
        logger.exception("Archive file could not be loaded")
        return HttpResponse("Datei konnte nicht geladen werden", status=500, content_type="text/plain")

    filename = f"{get_document_list_title(document)}.pdf"
    response = FileResponse(file_handle, content_type="application/pdf")
    response.headers["Content-Disposition"] = content_disposition_header(False, filename)
    return response
