from rest_framework.test import APITestCase

from django.contrib.auth.models import User
from django.contrib.admin.sites import AdminSite
from django.contrib.admin.options import ModelAdmin

from ..admin import CustomUserAdmin
from ..models import Profile
from ..factories import UserFactory


class AdminUserTests(APITestCase):

    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()

        Profile.objects.create(
            user=self.user,
            mobile='5149803840',
            phone='+15149803840',
        )

        Profile.objects.create(
            user=self.other_user,
            mobile='5146903840',
            phone='+15146903840',
        )

        self.site = AdminSite()

    def test_get_mobile(self):
        """
        Ensure we display the good mobile number in the user's admin panel
        """
        admin = CustomUserAdmin(User, self.site)
        self.assertEqual(
            admin.get_mobile(self.user),
            self.user.profile.mobile,
        )

    def test_get_phone(self):
        """
        Ensure we display the good phone number in the user's admin panel
        """
        admin = CustomUserAdmin(User, self.site)
        self.assertEqual(
            admin.get_phone(self.user),
            self.user.profile.phone,
        )
