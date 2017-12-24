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

    def test_is_active_property_true(self):
        """
        Ensure we have True if the cycle is active
        """
        start_date = timezone.now()
        end_date = start_date + timezone.timedelta(
            minutes=100,
        )

        cycle = Cycle.objects.create(
            name='my cycle',
            start_date=start_date,
            end_date=end_date,
        )

        self.assertEquals(cycle.is_active, True)

    def test_is_active_property_false(self):
        """
        Ensure we have False if the cycle is not active
        """
        start_date = timezone.now()
        end_date = start_date

        cycle = Cycle.objects.create(
            name='my cycle',
            start_date=start_date,
            end_date=end_date,
        )

        self.assertEquals(cycle.is_active, False)
