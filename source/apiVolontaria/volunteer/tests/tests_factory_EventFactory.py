from django.utils import timezone
from rest_framework.test import APITransactionTestCase

from ..factories import EventFactory, CellFactory, \
    CycleFactory, TaskTypeFactory


class EventFactoryTests(APITransactionTestCase):

    def setUp(self):
        self.now = timezone.now()
        self.future = self.now + timezone.timedelta(minutes=100)

    def test_create_object(self):
        self.obj = EventFactory()
        self.assertNotEqual(self.obj, None)
        self.assertNotEqual(self.obj.__str__(), None)

    def test_create_with_params(self):
        self.obj = EventFactory(
            start_date=self.now,
            end_date=self.future,
            nb_volunteers_needed=1,
            nb_volunteers_standby_needed=1,
            cell=CellFactory(),
            cycle=CycleFactory(),
            task_type=TaskTypeFactory(),

        )
        self.assertNotEqual(self.obj, None)
        self.assertEqual(self.obj.is_started, True)
        self.assertEqual(self.obj.is_expired, False)
        self.assertEqual(self.obj.is_active, True)
        self.assertNotEqual(self.obj.nb_volunteers, 1)
        self.assertNotEqual(self.obj.nb_volunteers_standby, 1)
