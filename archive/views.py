from __future__ import annotations

import logging

from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import redirect, render
from django.utils.http import content_disposition_header

from archive.files import open_archive_file
from archive.filters import filter_documents, get_semester_options, get_year_options
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


def base_context(request, main: str, current: str) -> dict:
    return {
        "protocol_type_labels": PROTOCOL_TYPE_LABELS,
        "statute_type_labels": STATUTE_TYPE_LABELS,
        "breadcrumb_main": main,
        "breadcrumb_current": current,
        "current_path": request.path,
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

    initial_documents = get_filtered_documents(
        DocumentFilters(doc_type="protokoll", convent_type=protocol_type)
    )

    search_term = request.GET.get("q", "")
    active_semester = request.GET.get("semester", "")
    active_year = request.GET.get("year", "")
    selected_id = request.GET.get("selected")

    documents = filter_documents(
        initial_documents,
        semester=active_semester or None,
        year=active_year or None,
        search_term=search_term,
    )

    selected_document = next(
        (document for document in initial_documents if str(document.id) == selected_id),
        None,
    )

    context = {
        **base_context(request, "Protokolle", PROTOCOL_TYPE_LABELS[protocol_type]),
        "title": PROTOCOL_TYPE_LABELS[protocol_type],
        "documents": documents,
        "document_count": len(documents),
        "selected_document": selected_document,
        "selected_panel": panel_context(selected_document) if selected_document else None,
        "semester_options": get_semester_options(initial_documents),
        "year_options": get_year_options(initial_documents),
        "search_term": search_term,
        "active_semester": active_semester,
        "active_year": active_year,
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
    except OSError:
        logger.exception("Archive file could not be opened")
        return HttpResponse(
            "Datei konnte nicht geladen werden",
            status=500,
            content_type="text/plain",
        )
    except ValueError:
        logger.exception("Unsafe archive path rejected")
        return HttpResponse(
            "Datei konnte nicht geladen werden",
            status=500,
            content_type="text/plain",
        )

    filename = f"{get_document_list_title(document)}.pdf"
    response = FileResponse(file_handle, content_type="application/pdf")
    response.headers["Content-Disposition"] = content_disposition_header(
        as_attachment=False,
        filename=filename,
    )
    return response
