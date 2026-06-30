from __future__ import annotations

from dataclasses import asdict, dataclass

from django.core.cache import cache
from django.db.models import F

from archive.labels import DocumentData, ListDocument, calc_semester, get_document_list_title, to_date_only
from archive.models import Document


@dataclass(frozen=True)
class DocumentFilters:
    doc_type: str | None = None
    convent_type: str | None = None
    year: int | None = None


def document_to_data(document: Document) -> DocumentData:
    return DocumentData(
        id=document.id,
        doc_type=document.doc_type,
        convent_type=document.convent_type,
        is_extraordinary=document.is_extraordinary,
        convent_number=document.convent_number,
        version_date=to_date_only(document.version_date),
        uploaded_at=to_date_only(document.uploaded_at),
        archive_path=document.archive_path,
        file_size_bytes=document.file_size_bytes,
    )


def document_to_list_data(document: Document) -> ListDocument:
    data = document_to_data(document)
    return ListDocument(
        **asdict(data),
        semester=calc_semester(data.version_date),
        title=get_document_list_title(data),
    )


def get_filtered_documents(filters: DocumentFilters) -> list[ListDocument]:
    queryset = Document.objects.all()

    if filters.doc_type:
        queryset = queryset.filter(doc_type=filters.doc_type.lower())

    if filters.convent_type:
        convent_type = filters.convent_type.lower()

        if convent_type == "ao":
            queryset = queryset.filter(is_extraordinary=True)
        else:
            queryset = queryset.filter(convent_type=convent_type)

    if filters.year:
        queryset = queryset.filter(version_date__year=filters.year)

    queryset = queryset.order_by("-version_date", F("convent_number").desc(nulls_last=True))[:200]

    return [document_to_list_data(document) for document in queryset]


def get_document_by_id(document_id: int) -> DocumentData | None:
    document = Document.objects.filter(id=document_id).first()
    return document_to_data(document) if document else None


def get_single_document_by_doc_type(doc_type: str) -> DocumentData | None:
    document = Document.objects.filter(doc_type=doc_type).order_by("-version_date").first()
    return document_to_data(document) if document else None


def get_cached_single_document_by_doc_type(doc_type: str) -> DocumentData | None:
    cache_key = f"single-document-by-doc-type:{doc_type}"
    cached_document = cache.get(cache_key)

    if cached_document is not None:
        return cached_document

    document = get_single_document_by_doc_type(doc_type)
    cache.set(cache_key, document, timeout=60 * 60 * 24)
    return document
