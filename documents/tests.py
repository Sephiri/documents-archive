from datetime import date
from types import SimpleNamespace

from django.test import SimpleTestCase

from members.models import Member

from .permissions import can_view_document


class DocumentPermissionTests(SimpleTestCase):
    def test_fux_cannot_view_protocol(self):
        member = SimpleNamespace(
            joined_at=date(2020, 1, 1),
            status=Member.Status.FUX,
        )
        document = SimpleNamespace(
            version_date=date(2024, 1, 1),
            doc_type="protokoll",
        )

        self.assertFalse(can_view_document(member, document))

    def test_fux_can_view_satzung_after_join_date(self):
        member = SimpleNamespace(
            joined_at=date(2020, 1, 1),
            status=Member.Status.FUX,
        )
        document = SimpleNamespace(
            version_date=date(2024, 1, 1),
            doc_type="satzung",
        )

        self.assertTrue(can_view_document(member, document))

    def test_dame_can_view_protocol_after_join_date(self):
        member = SimpleNamespace(
            joined_at=date(2020, 1, 1),
            status=Member.Status.DAME,
        )
        document = SimpleNamespace(
            version_date=date(2024, 1, 1),
            doc_type="protokoll",
        )

        self.assertTrue(can_view_document(member, document))

    def test_member_cannot_view_document_before_join_date(self):
        member = SimpleNamespace(
            joined_at=date(2024, 1, 1),
            status=Member.Status.DAME,
        )
        document = SimpleNamespace(
            version_date=date(2020, 1, 1),
            doc_type="satzung",
        )

        self.assertFalse(can_view_document(member, document))
