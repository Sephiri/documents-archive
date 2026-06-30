from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.test import SimpleTestCase, override_settings
from django.urls import reverse

from archive.files import get_safe_archive_path
from archive.filters import filter_documents, get_semester_options, get_year_options
from archive.labels import DocumentData, ListDocument, calc_semester, format_file_size, get_document_list_title


def make_document() -> DocumentData:
    return DocumentData(
        id=7,
        doc_type="satzung",
        convent_type=None,
        is_extraordinary=None,
        convent_number=None,
        version_date="2026-06-06",
        uploaded_at="2026-06-07",
        archive_path="data/archive/test.pdf",
        file_size_bytes=2048,
    )


def make_list_document(
    document_id: int = 7,
    convent_type: str = "ac",
    convent_number: int = 2,
    version_date: str = "2026-06-06",
    semester: str = "SS26",
) -> ListDocument:
    document = DocumentData(
        id=document_id,
        doc_type="protokoll",
        convent_type=convent_type,
        is_extraordinary=False,
        convent_number=convent_number,
        version_date=version_date,
        uploaded_at=version_date,
        archive_path=f"data/archive/{document_id}.pdf",
        file_size_bytes=2048,
    )
    return ListDocument(
        **document.__dict__,
        semester=semester,
        title=get_document_list_title(document),
        uploaded_at_formatted="06.06.2026",
    )


class LabelTests(SimpleTestCase):
    def test_calc_semester(self):
        self.assertEqual(calc_semester("2026-06-06"), "SS26")
        self.assertEqual(calc_semester("2026-01-06"), "WS25/26")
        self.assertEqual(calc_semester("2026-10-06"), "WS26/27")

    def test_protocol_title(self):
        self.assertEqual(get_document_list_title(make_list_document()), "2. AC 06.06.2026")

    def test_statute_title(self):
        self.assertEqual(get_document_list_title(make_document()), "Satzung")

    def test_format_file_size(self):
        self.assertEqual(format_file_size(None), "Unbekannt")
        self.assertEqual(format_file_size(42), "42 B")
        self.assertEqual(format_file_size(2048), "2.0 KB")


class FilterTests(SimpleTestCase):
    def setUp(self):
        self.documents = [
            make_list_document(1, "ac", 1, "2026-06-01", "SS26"),
            make_list_document(2, "ac", 2, "2025-11-01", "WS25/26"),
            make_list_document(3, "cc", 3, "2025-05-01", "SS25"),
        ]

    def test_options(self):
        self.assertEqual(get_year_options(self.documents), ["2026", "2025"])
        self.assertEqual(get_semester_options(self.documents), ["SS25", "SS26", "WS25/26"])

    def test_filter_by_semester(self):
        filtered = filter_documents(self.documents, semester="SS26")
        self.assertEqual([document.id for document in filtered], [1])

    def test_filter_by_year(self):
        filtered = filter_documents(self.documents, year="2025")
        self.assertEqual([document.id for document in filtered], [2, 3])

    def test_filter_by_search_term(self):
        filtered = filter_documents(self.documents, search_term="2. ac")
        self.assertEqual([document.id for document in filtered], [2])


class FilePathTests(SimpleTestCase):
    def test_safe_archive_path_stays_inside_archive_root(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            with override_settings(ARCHIVE_ROOT=str(root)):
                result = get_safe_archive_path("data/archive/test.pdf")

            self.assertEqual(result, root / "data" / "archive" / "test.pdf")

    def test_rejects_absolute_paths(self):
        with self.assertRaises(ValueError):
            get_safe_archive_path("/etc/passwd")

    def test_rejects_path_traversal(self):
        with TemporaryDirectory() as temp_dir:
            with override_settings(ARCHIVE_ROOT=temp_dir):
                with self.assertRaises(ValueError):
                    get_safe_archive_path("../secret.pdf")


class ViewTests(SimpleTestCase):
    @patch("archive.views.get_cached_single_document_by_doc_type")
    def test_statute_view_renders_document_panel(self, get_document):
        get_document.return_value = make_document()
        response = self.client.get(reverse("statute-view", args=["satzung"]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Satzung")
        self.assertContains(response, reverse("file-view", args=[7]))

    @patch("archive.views.get_filtered_documents")
    def test_protocol_view_renders_documents_data(self, get_documents):
        get_documents.return_value = [make_list_document()]
        response = self.client.get(reverse("protocol-view", args=["ac"]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AC-Protokolle")
        self.assertContains(response, "2. AC 06.06.2026")

    @patch("archive.views.open_archive_file")
    @patch("archive.views.get_document_by_id")
    def test_file_view_streams_pdf(self, get_document, open_file):
        get_document.return_value = make_document()
        open_file.return_value = BytesIO(b"%PDF-1.4")
        response = self.client.get(reverse("file-view", args=[7]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertIn("inline", response["Content-Disposition"])
        self.assertEqual(b"".join(response.streaming_content), b"%PDF-1.4")

    @patch("archive.views.get_document_by_id")
    def test_file_view_returns_404_for_missing_file(self, get_document):
        get_document.return_value = None
        response = self.client.get(reverse("file-view", args=[7]))

        self.assertEqual(response.status_code, 404)
