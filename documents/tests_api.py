from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase
from django.utils import timezone

from members.models import Member

from .models import Document


class DocumentApiTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(Document)

    @classmethod
    def tearDownClass(cls):
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(Document)
        super().tearDownClass()

    def create_user(self, email="user@example.com"):
        User = get_user_model()
        return User.objects.create_user(
            email=email,
            password="test-password",
        )

    def create_member(
        self,
        *,
        user=None,
        email="member@example.com",
        status=Member.Status.DAME,
        joined_at=date(2020, 1, 1),
        is_current_member=True,
    ):
        return Member.objects.create(
            user=user,
            email=email,
            first_name="Test",
            last_name="Member",
            joined_at=joined_at,
            joined_semester=Member.Semester.WS,
            joined_semester_year=2019,
            status=status,
            is_current_member=is_current_member,
        )

    def create_document(
        self,
        *,
        hash_value="hash-1",
        doc_type="protokoll",
        convent_type="ac",
        version_date=date(2024, 1, 1),
    ):
        return Document.objects.create(
            hash=hash_value,
            doc_type=doc_type,
            convent_type=convent_type,
            version_date=version_date,
            archive_path=f"{hash_value}.pdf",
            content_md="",
            metadata={},
            is_extraordinary=False,
            convent_number=1,
            uploaded_at=timezone.now(),
            file_size_bytes=1234,
        )

    def test_anonymous_user_is_redirected(self):
        response = self.client.get("/api/documents/")

        self.assertEqual(response.status_code, 302)

    def test_logged_in_user_without_member_gets_403(self):
        user = self.create_user(email="user@example.com")
        self.client.force_login(user)

        response = self.client.get("/api/documents/")

        self.assertEqual(response.status_code, 403)

    def test_inactive_member_gets_403(self):
        user = self.create_user(email="inactive@example.com")
        self.create_member(
            user=user,
            email="inactive@example.com",
            is_current_member=False,
        )
        self.client.force_login(user)

        response = self.client.get("/api/documents/")

        self.assertEqual(response.status_code, 403)

    def test_dame_can_access_documents_api(self):
        user = self.create_user(email="dame@example.com")
        self.create_member(
            user=user,
            email="dame@example.com",
            status=Member.Status.DAME,
        )
        self.create_document(
            hash_value="protocol-1",
            doc_type="protokoll",
            convent_type="ac",
        )

        self.client.force_login(user)

        response = self.client.get("/api/documents/")

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertEqual(len(data["documents"]), 1)
        self.assertEqual(data["documents"][0]["doc_type"], "protokoll")
        self.assertEqual(data["documents"][0]["convent_type"], "ac")
        self.assertTrue(data["documents"][0]["can_view"])
        self.assertIsNotNone(data["documents"][0]["file_url"])
        self.assertIsNotNone(data["documents"][0]["download_url"])

    def test_fux_sees_protocol_as_locked(self):
        user = self.create_user(email="fux@example.com")
        self.create_member(
            user=user,
            email="fux@example.com",
            status=Member.Status.FUX,
        )
        self.create_document(
            hash_value="protocol-locked",
            doc_type="protokoll",
            convent_type="ac",
        )

        self.client.force_login(user)

        response = self.client.get("/api/documents/")

        self.assertEqual(response.status_code, 200)

        data = response.json()
        document = data["documents"][0]

        self.assertEqual(document["doc_type"], "protokoll")
        self.assertFalse(document["can_view"])
        self.assertIsNone(document["file_url"])
        self.assertIsNone(document["download_url"])

    def test_document_before_join_date_is_locked(self):
        user = self.create_user(email="late@example.com")
        self.create_member(
            user=user,
            email="late@example.com",
            status=Member.Status.DAME,
            joined_at=date(2024, 1, 1),
        )
        self.create_document(
            hash_value="old-satzung",
            doc_type="satzung",
            convent_type=None,
            version_date=date(2020, 1, 1),
        )

        self.client.force_login(user)

        response = self.client.get("/api/documents/")

        self.assertEqual(response.status_code, 200)

        document = response.json()["documents"][0]

        self.assertEqual(document["doc_type"], "satzung")
        self.assertFalse(document["can_view"])
        self.assertIsNone(document["file_url"])
        self.assertIsNone(document["download_url"])

    def test_documents_api_filter_by_doc_type_and_convent_type(self):
        user = self.create_user(email="filter@example.com")
        self.create_member(
            user=user,
            email="filter@example.com",
            status=Member.Status.DAME,
        )

        self.create_document(
            hash_value="ac-protocol",
            doc_type="protokoll",
            convent_type="ac",
        )
        self.create_document(
            hash_value="dac-protocol",
            doc_type="protokoll",
            convent_type="dac",
        )
        self.create_document(
            hash_value="satzung",
            doc_type="satzung",
            convent_type=None,
        )

        self.client.force_login(user)

        response = self.client.get("/api/documents/?doc_type=protokoll&convent_type=ac")

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertEqual(len(data["documents"]), 1)
        self.assertEqual(data["documents"][0]["hash"], "ac-protocol")

    def setUp(self):
        self.archive_root = TemporaryDirectory()

    def tearDown(self):
        self.archive_root.cleanup()

    def create_pdf_file(self, filename):
        file_path = Path(self.archive_root.name) / filename
        file_path.write_bytes(b"%PDF-1.4\n% test pdf\n")
        return file_path

    def test_dame_can_access_document_file(self):
        user = self.create_user(email="file-dame@example.com")
        self.create_member(
            user=user,
            email="file-dame@example.com",
            status=Member.Status.DAME,
        )

        self.create_pdf_file("allowed.pdf")

        document = self.create_document(
            hash_value="allowed-file",
            doc_type="protokoll",
            convent_type="ac",
        )
        document.archive_path = "allowed.pdf"
        document.save(update_fields=["archive_path"])

        self.client.force_login(user)

        with self.settings(ARCHIVE_ROOT=self.archive_root.name):
            response = self.client.get(f"/intern/documents/{document.pk}/file/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")

    def test_fux_cannot_access_protocol_file_directly(self):
        user = self.create_user(email="file-fux@example.com")
        self.create_member(
            user=user,
            email="file-fux@example.com",
            status=Member.Status.FUX,
        )

        self.create_pdf_file("locked.pdf")

        document = self.create_document(
            hash_value="locked-file",
            doc_type="protokoll",
            convent_type="ac",
        )
        document.archive_path = "locked.pdf"
        document.save(update_fields=["archive_path"])

        self.client.force_login(user)

        with self.settings(ARCHIVE_ROOT=self.archive_root.name):
            response = self.client.get(f"/intern/documents/{document.pk}/file/")

        self.assertEqual(response.status_code, 403)

    def test_member_cannot_access_file_before_join_date(self):
        user = self.create_user(email="late-file@example.com")
        self.create_member(
            user=user,
            email="late-file@example.com",
            status=Member.Status.DAME,
            joined_at=date(2024, 1, 1),
        )

        self.create_pdf_file("old.pdf")

        document = self.create_document(
            hash_value="old-file",
            doc_type="satzung",
            convent_type=None,
            version_date=date(2020, 1, 1),
        )
        document.archive_path = "old.pdf"
        document.save(update_fields=["archive_path"])

        self.client.force_login(user)

        with self.settings(ARCHIVE_ROOT=self.archive_root.name):
            response = self.client.get(f"/intern/documents/{document.pk}/file/")

        self.assertEqual(response.status_code, 403)
