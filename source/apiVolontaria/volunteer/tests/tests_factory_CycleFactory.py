from django.utils import timezone
from rest_framework.test import APITransactionTestCase

from ..factories import CycleFactory


class CycleFactoryTests(APITransactionTestCase):

    def setUp(self):
        self.now = timezone.now()
        self.future = self.now + timezone.timedelta(minutes=100)

    def test_create_object(self):
        self.obj = CycleFactory()
        self.assertNotEqual(self.obj, None)
        self.assertNotEqual(self.obj.__str__(), None)

    def test_create_with_name(self):
        self.obj = CycleFactory(name='New Cycle')
        self.assertNotEqual(self.obj, None)

    def test_create_with_dates(self):
        self.obj = CycleFactory(
            start_date=self.now,
            end_date=self.future,
        )
        self.assertNotEqual(self.obj, None)
        self.assertEqual(self.obj.is_active, True)
