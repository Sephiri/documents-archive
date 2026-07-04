from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import Member


class MemberApiTests(TestCase):
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
        first_name="Anna",
        last_name="Beispiel",
        status=Member.Status.DAME,
        is_current_member=True,
    ):
        return Member.objects.create(
            user=user,
            email=email,
            first_name=first_name,
            last_name=last_name,
            joined_at=date(2024, 1, 1),
            joined_semester=Member.Semester.WS,
            joined_semester_year=2023,
            status=status,
            is_current_member=is_current_member,
        )

    def test_anonymous_user_is_redirected(self):
        response = self.client.get("/api/members/")

        self.assertEqual(response.status_code, 302)

    def test_logged_in_user_without_member_gets_403(self):
        user = self.create_user(email="user@example.com")
        self.client.force_login(user)

        response = self.client.get("/api/members/")

        self.assertEqual(response.status_code, 403)

    def test_inactive_member_gets_403(self):
        user = self.create_user(email="inactive@example.com")
        self.create_member(
            user=user,
            email="inactive@example.com",
            is_current_member=False,
        )
        self.client.force_login(user)

        response = self.client.get("/api/members/")

        self.assertEqual(response.status_code, 403)

    def test_current_member_can_access_member_api(self):
        user = self.create_user(email="active@example.com")
        self.create_member(
            user=user,
            email="active@example.com",
            first_name="Active",
            last_name="Member",
        )

        self.create_member(
            email="former@example.com",
            first_name="Former",
            last_name="Member",
            is_current_member=False,
        )

        self.client.force_login(user)

        response = self.client.get("/api/members/")

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertEqual(len(data["members"]), 1)
        self.assertEqual(data["members"][0]["email"], "active@example.com")
        self.assertEqual(data["members"][0]["display_name"], "Active Member")

    def test_member_api_status_filter(self):
        user = self.create_user(email="dame@example.com")
        self.create_member(
            user=user,
            email="dame@example.com",
            first_name="Dame",
            last_name="Member",
            status=Member.Status.DAME,
        )

        self.create_member(
            email="fux@example.com",
            first_name="Fux",
            last_name="Member",
            status=Member.Status.FUX,
        )

        self.client.force_login(user)

        response = self.client.get("/api/members/?status=FUX")

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertEqual(len(data["members"]), 1)
        self.assertEqual(data["members"][0]["email"], "fux@example.com")
        self.assertEqual(data["members"][0]["status"], Member.Status.FUX)

    def test_member_api_does_not_expose_private_contact_fields(self):
        user = self.create_user(email="private@example.com")
        self.create_member(
            user=user,
            email="private@example.com",
        )
        self.client.force_login(user)

        response = self.client.get("/api/members/")

        self.assertEqual(response.status_code, 200)

        member_data = response.json()["members"][0]

        self.assertNotIn("phone", member_data)
        self.assertNotIn("address_line", member_data)
        self.assertNotIn("postal_code", member_data)
        self.assertNotIn("city", member_data)
