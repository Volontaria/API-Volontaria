from rest_framework.test import APITestCase

from volunteer.models import TaskType


class TaskTypeTests(APITestCase):

    def setUp(self):
        pass

    def test_str_method(self):
        """
        Validate the string representation of tasktypes
        """

        tasktype = TaskType.objects.create(
            name='TaskType 1',
        )

        self.assertEqual(str(tasktype), tasktype.name)
