from django.contrib.auth.models import User
from rest_framework.test import APITransactionTestCase

from django.contrib.admin.sites import AdminSite
from django.test import Client

from apiVolontaria.models import Profile

from ..factories import UserFactory
from ..admin import CustomUserAdmin


class UserAdminTests(APITransactionTestCase):

    def setUp(self):
        self.create_users()

        self.site = AdminSite()
        self.admin = CustomUserAdmin(User, self.site)

    def create_users(self):
        self.user = UserFactory()
        self.user.set_password('Test123!')
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.is_active = True
        self.user.save()

        profile = Profile(
            user=self.user,
            phone='1234567890',
            mobile='0987654321',
            volunteer_note='testNote',
        )

        profile.save()

        self.user_no_profile = UserFactory()
        self.user_no_profile.set_password('Test123!')
        self.user_no_profile.save()

    def test_get_profile_note(self):
        self.assertEqual(self.admin.get_profile_note(self.user), self.user.profile.volunteer_note)

        self.assertEqual(self.admin.get_profile_note(self.user_no_profile), '')

    def test_admin_user_listing(self):
        client = Client()
        client.login(username=self.user.username, password='Test123!')

        admin_pages = [
            "/admin/auth/user/",
        ]

        for page in admin_pages:
            resp = client.get(page)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("<!DOCTYPE html", str(resp.content))
