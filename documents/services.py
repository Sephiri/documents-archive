from django.db.models import Q

from .models import Document
from .permissions import can_view_document

ALLOWED_DOCUMENT_SORTS = {
    "-version_date",
    "version_date",
    "-uploaded_at",
    "uploaded_at",
    "doc_type",
    "convent_type",
}


def get_filtered_documents(*, member, q="", doc_type="", convent_type="", sort="-version_date"):
    documents = Document.objects.all()

    if q:
        documents = documents.filter(Q(doc_type__icontains=q) | Q(convent_type__icontains=q) | Q(archive_path__icontains=q))

    if doc_type:
        documents = documents.filter(doc_type=doc_type)

    if convent_type:
        documents = documents.filter(convent_type=convent_type)

    if sort not in ALLOWED_DOCUMENT_SORTS:
        sort = "-version_date"

    documents = documents.order_by(sort)

    for document in documents:
        document.can_view = can_view_document(member, document)

    return documents


def get_document_filter_options():
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

    return {
        "doc_types": doc_types,
        "convent_types": convent_types,
    }
