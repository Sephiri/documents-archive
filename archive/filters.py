from archive.labels import ListDocument


def get_semester_options(documents: list[ListDocument]) -> list[str]:
    return sorted({document.semester for document in documents})


def get_year_options(documents: list[ListDocument]) -> list[str]:
    return sorted(
        {document.version_date.split("-", 1)[0] for document in documents},
        key=int,
        reverse=True,
    )


def filter_documents(
    documents: list[ListDocument],
    semester: str | None = None,
    year: str | None = None,
    search_term: str | None = None,
) -> list[ListDocument]:
    normalized_search = (search_term or "").strip().lower()

    filtered_documents = []
    for document in documents:
        matches_semester = not semester or document.semester == semester
        matches_year = not year or document.version_date.startswith(year)
        matches_search = not normalized_search or normalized_search in document.title.lower()

        if matches_semester and matches_year and matches_search:
            filtered_documents.append(document)

    return filtered_documents
