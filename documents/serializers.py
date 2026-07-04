from django.urls import reverse


def serialize_document(document):
    can_view = getattr(document, "can_view", False)

    return {
        "id": document.pk,
        "hash": document.hash,
        "doc_type": document.doc_type,
        "convent_type": document.convent_type,
        "version_date": document.version_date.isoformat(),
        "archive_path": document.archive_path,
        "is_extraordinary": document.is_extraordinary,
        "convent_number": document.convent_number,
        "uploaded_at": document.uploaded_at.isoformat(),
        "file_size_bytes": document.file_size_bytes,
        "can_view": can_view,
        "file_url": reverse("documents:document_file", args=[document.pk]) if can_view else None,
        "download_url": reverse("documents:document_download", args=[document.pk]) if can_view else None,
    }
