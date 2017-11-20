from rest_framework.test import APITestCase

from volunteer.models import Cycle
from django.utils import timezone


class CycleTests(APITestCase):

    def setUp(self):
        pass

    def test_create_cycle(self):
        """
        Ensure we can create a new cycle with just required arguments
        """
        token = Cycle.objects.create(
            name='my cycle'
        )

        self.assertEquals(token.name, 'my cycle')
