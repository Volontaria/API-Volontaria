from rest_framework.test import APITransactionTestCase

from ..factories import TaskTypeFactory


class TaskTypeFactoryTests(APITransactionTestCase):

    def setUp(self):
        pass

    def test_create_task_type(self):
        self.obj = TaskTypeFactory()
        self.assertNotEqual(self.obj, None)
        self.assertNotEqual(self.obj.__str__(), None)

    def test_create_task_type_with_name(self):
        self.obj = TaskTypeFactory(name="New TaskType")
        self.assertNotEqual(self.obj, None)
