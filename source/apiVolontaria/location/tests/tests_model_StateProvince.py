from rest_framework.test import APITestCase

from location.models import Country, StateProvince


class StateProvinceTests(APITestCase):

    def setUp(self):
        self.random_country = Country.objects.create(name="random country")

    def test_create_state(self):
        """
        Ensure we can create a new state with just required arguments
        """
        params = dict(
            name="random state",
            country=self.random_country,
        )

        new_state = StateProvince.objects.create(**params)

        self.assertEqual(str(new_state), "random state, random country")
        self.assertEqual(new_state.name, params['name'])
        self.assertFalse(new_state.iso_code)
