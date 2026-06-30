from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any


PROTOCOL_TYPE_LABELS = {
    "av": "AV-Protokolle",
    "ac": "AC-Protokolle",
    "dac": "DaC-Protokolle",
    "cc": "CC-Protokolle",
}

STATUTE_TYPE_LABELS = {
    "satzung": "Satzung",
    "vereinsordnung": "Vereinsordnung (VO)",
    "beschlussbuch": "Beschlussbuch",
    "fuxenfibel": "Fuxenfibel",
}

DOC_TYPE_LABELS = {
    "protokoll": "Protokoll",
    "satzung": "Satzung",
    "vereinsordnung": "Vereinsordnung",
    "beschlussbuch": "Beschlussbuch",
    "fuxenfibel": "Fuxenfibel",
}

CONVENT_TYPE_LABELS = {
    "ac": "AC",
    "cc": "CC",
    "dac": "DaC",
    "dc": "DC",
    "av": "AV",
}


@dataclass(frozen=True)
class DocumentData:
    id: int
    doc_type: str
    convent_type: str | None
    is_extraordinary: bool | None
    convent_number: int | None
    version_date: str
    uploaded_at: str
    archive_path: str | None
    file_size_bytes: int | None


@dataclass(frozen=True)
class ListDocument(DocumentData):
    semester: str
    title: str


def is_protocol_type(value: str) -> bool:
    return value in PROTOCOL_TYPE_LABELS


def is_statute_type(value: str) -> bool:
    return value in STATUTE_TYPE_LABELS


def to_date_only(value: str | date | datetime) -> str:
    if isinstance(value, datetime):
        return value.date().isoformat()

    if isinstance(value, date):
        return value.isoformat()

    return value


def parse_date_only(value: str | date | datetime) -> date:
    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    return date.fromisoformat(value)


def calc_semester(value: str | date | datetime) -> str:
    current_date = parse_date_only(value)
    year = current_date.year
    month = current_date.month
    short_year = year % 100

    if 4 <= month <= 9:
        return f"SS{short_year:02d}"

    if month <= 3:
        return f"WS{(year - 1) % 100:02d}/{short_year:02d}"

    return f"WS{short_year:02d}/{(year + 1) % 100:02d}"


def get_doc_type_label(doc_type: str) -> str:
    return DOC_TYPE_LABELS.get(doc_type, doc_type)


def get_convent_type_label(convent_type: str | None, is_extraordinary: bool | None = False) -> str | None:
    if not convent_type:
        return None

    base_label = CONVENT_TYPE_LABELS.get(convent_type, convent_type)
    return f"ao{base_label}" if is_extraordinary else base_label


def format_date(value: str | date | datetime) -> str:
    return parse_date_only(value).strftime("%d.%m.%Y")


def format_file_size(bytes_value: int | None) -> str:
    if bytes_value is None:
        return "Unbekannt"

    if bytes_value < 1024:
        return f"{bytes_value} B"

    if bytes_value < 1024 * 1024:
        return f"{bytes_value / 1024:.1f} KB"

    return f"{bytes_value / 1024 / 1024:.1f} MB"


def get_value(document: Any, key: str) -> Any:
    if isinstance(document, dict):
        return document.get(key)

    return getattr(document, key)


def get_document_list_title(document: Any) -> str:
    doc_type = get_value(document, "doc_type")

    if doc_type != "protokoll":
        return get_doc_type_label(doc_type)

    parts = [
        f"{get_value(document, 'convent_number')}." if get_value(document, "convent_number") else None,
        get_convent_type_label(get_value(document, "convent_type"), get_value(document, "is_extraordinary")),
        format_date(get_value(document, "version_date")),
    ]

    return " ".join(part for part in parts if part)


def build_document_meta_items(document: DocumentData) -> list[str]:
    items = ["Zugriffsstatus: Alle Mitglieder"]

    if document.doc_type != "protokoll":
        label = "Letzte Änderung" if document.doc_type == "fuxenfibel" else "Beschlossen am"
        items.append(f"{label}: {format_date(document.version_date)} im {calc_semester(document.version_date)}")

    items.append(f"Hochgeladen: {format_date(document.uploaded_at)}")
    items.append(f"Größe: {format_file_size(document.file_size_bytes)}")

    return items
