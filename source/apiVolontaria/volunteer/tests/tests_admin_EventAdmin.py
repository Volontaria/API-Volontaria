from django.contrib.auth.models import User
from rest_framework.test import APITransactionTestCase

from django.contrib.admin.sites import AdminSite
from django.test import Client

from apiVolontaria.models import Profile
from ..admin import EventAdmin
from ..models import Event


class EventAdminTests(APITransactionTestCase):

    def setUp(self):
        self.create_user()

        self.site = AdminSite()
        self.admin = EventAdmin(Event, self.site)

    def create_user(self):
        self.username = "test_admin"
        self.password = User.objects.make_random_password()
        user, created = User.objects.get_or_create(username=self.username)
        user.set_password(self.password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()
        self.user = user

        profile = Profile(
            user=user,
            phone='1234567890',
            mobile='0987654321'
        )

        profile.save()

    def test_admin_access(self):
        client = Client()
        client.login(username=self.username, password=self.password)

        admin_pages = [
            "/admin/volunteer/",
            "/admin/volunteer/event/",
            ]

        for page in admin_pages:
            resp = client.get(page)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("<!DOCTYPE html", str(resp.content))

    def test_admin_events(self):
        self.assertNotEqual(self.admin, None)
