from rest_framework.test import APITestCase
from django.core.exceptions import ValidationError

from ..models import Profile
from ..factories import UserFactory


class ProfileTests(APITestCase):

    def setUp(self):
        self.user = UserFactory()

    def test_bad_format_phone(self):
        """
        Ensure we can't store a bad format of phone number
        """
        params = dict(
            user=self.user,
            # two digits in excess
            phone="+3361122334455"
        )

        with self.assertRaisesRegex(
                ValidationError,
                'The phone field need to be in a valid format'
        ):
            Profile.objects.create(**params)

    def test_local_format_phone(self):
        """
        Ensure we can't store a bad format of phone number
        """
        profile = Profile.objects.create(
            user=self.user,
            phone="5141231234"
        )

        self.assertEquals(profile.phone, "5141231234")

    def test_one_digit_international_format_phone(self):
        """
        Ensure we can store an american format of phone number
        """
        profile = Profile.objects.create(
            user=self.user,
            phone="+15141231234"
        )

        self.assertEquals(profile.phone, "+15141231234")

    def test_two_digit_international_format_phone(self):
        """
        Ensure we can store an european format of phone number
        """
        profile = Profile.objects.create(
            user=self.user,
            phone="+33601020304"
        )

        self.assertEquals(profile.phone, "+33601020304")

    def test_good_format_phone_with_space(self):
        """
        Ensure we can store a phone number with space in it
        """
        profile = Profile.objects.create(
            user=self.user,
            phone="+33 6 01 02 03 04"
        )

        self.assertEquals(profile.phone, "+33601020304")

    def test_good_format_phone_with_dash(self):
        """
        Ensure we can store a phone number with dash in it
        """
        profile = Profile.objects.create(
            user=self.user,
            phone="+33-6-01-02-03-04"
        )

        self.assertEquals(profile.phone, "+33601020304")

    def test_good_format_phone_with_dot(self):
        """
        Ensure we can store a phone number with dot in it
        """
        profile = Profile.objects.create(
            user=self.user,
            phone="+33.6.01.02.03.04"
        )

        self.assertEquals(profile.phone, "+33601020304")

    def test_good_format_phone_with_parenthesis(self):
        """
        Ensure we can store a phone number with parenthesis in it
        """
        profile = Profile.objects.create(
            user=self.user,
            phone="(+33)601020304"
        )

        self.assertEquals(profile.phone, "+33601020304")

    def test_canadian_format_phone(self):
        """
        Ensure we can store a phone number in canadian format
        """
        profile = Profile.objects.create(
            user=self.user,
            phone="(514)-980-3840"
        )

        self.assertEquals(profile.phone, "5149803840")

    def test_bad_format_mobile(self):
        """
        Ensure we can't store a bad format of mobile number
        """
        params = dict(
            user=self.user,
            # two digits in excess
            mobile="+3361122334455"
        )

        with self.assertRaisesRegex(
                ValidationError,
                'The mobile field need to be in a valid format'
        ):
            Profile.objects.create(**params)

    def test_local_format_mobile(self):
        """
        Ensure we can't store a bad format of mobile number
        """
        profile = Profile.objects.create(
            user=self.user,
            mobile="5141231234"
        )

        self.assertEquals(profile.mobile, "5141231234")

    def test_one_digit_international_format_mobile(self):
        """
        Ensure we can store an american format of mobile number
        """
        profile = Profile.objects.create(
            user=self.user,
            mobile="+15141231234"
        )

        self.assertEquals(profile.mobile, "+15141231234")

    def test_two_digit_international_format_mobile(self):
        """
        Ensure we can store an european format of mobile number
        """
        profile = Profile.objects.create(
            user=self.user,
            mobile="+33601020304"
        )

        self.assertEquals(profile.mobile, "+33601020304")

    def test_good_format_mobile_with_space(self):
        """
        Ensure we can store a mobile number with space in it
        """
        profile = Profile.objects.create(
            user=self.user,
            mobile="+33 6 01 02 03 04"
        )

        self.assertEquals(profile.mobile, "+33601020304")

    def test_good_format_mobile_with_dash(self):
        """
        Ensure we can store a mobile number with dash in it
        """
        profile = Profile.objects.create(
            user=self.user,
            mobile="+33-6-01-02-03-04"
        )

        self.assertEquals(profile.mobile, "+33601020304")

    def test_good_format_mobile_with_dot(self):
        """
        Ensure we can store a mobile number with dot in it
        """
        profile = Profile.objects.create(
            user=self.user,
            mobile="+33.6.01.02.03.04"
        )

        self.assertEquals(profile.mobile, "+33601020304")

    def test_good_format_mobile_with_parenthesis(self):
        """
        Ensure we can store a mobile number with parenthesis in it
        """
        profile = Profile.objects.create(
            user=self.user,
            mobile="(+33)601020304"
        )

        self.assertEquals(profile.mobile, "+33601020304")

    def test_canadian_format_mobile(self):
        """
        Ensure we can store a mobile number in canadian format
        """
        profile = Profile.objects.create(
            user=self.user,
            mobile="(514)-980-3840"
        )

        self.assertEquals(profile.mobile, "5149803840")
