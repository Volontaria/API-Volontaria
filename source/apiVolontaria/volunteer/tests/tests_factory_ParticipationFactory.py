from django.utils import timezone
from rest_framework.test import APITransactionTestCase

from apiVolontaria.factories import UserFactory
from ..factories import ParticipationFactory, EventFactory


class ParticipationFactoryTests(APITransactionTestCase):

    def setUp(self):
        self.now = timezone.now()
        self.future = self.now + timezone.timedelta(minutes=100)

    def test_create_object(self):
        self.obj = ParticipationFactory()
        self.assertNotEqual(self.obj, None)
        self.assertNotEqual(self.obj.__str__(), None)

    def test_create_with_params(self):
        event = EventFactory()

        self.obj = ParticipationFactory(
            event=event,
            user=UserFactory(),
            standby=False,
            subscription_date=self.now

        )
        self.assertNotEqual(self.obj, None)
        self.assertIsNotNone(self.obj.start_date)
        self.assertIsNotNone(self.obj.end_date)
        self.assertIsNotNone(self.obj.cell)
