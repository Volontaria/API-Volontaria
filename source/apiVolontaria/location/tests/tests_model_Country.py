from rest_framework.test import APITestCase

from location.models import Country


class CountryTests(APITestCase):

    def setUp(self):
        pass

    def test_create_country(self):
        """
        Ensure we can create a new country with just required arguments
        """
        params = dict(
            name="random country",
        )

        new_country = Country.objects.create(**params)

        self.assertEqual(str(new_country), "random country")
        self.assertEqual(new_country.name, params['name'])
        self.assertFalse(new_country.iso_code)
