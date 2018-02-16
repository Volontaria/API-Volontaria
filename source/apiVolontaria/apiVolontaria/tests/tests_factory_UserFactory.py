from rest_framework.test import APITransactionTestCase

from ..factories import UserFactory


class UserFactoryTests(APITransactionTestCase):

    def setUp(self):
        pass

    def test_create_object(self):
        self.obj = UserFactory()
        self.assertNotEqual(self.obj, None)

    def test_create_with_params(self):
        self.obj = UserFactory(
            first_name='Luke',
            last_name='Skywalker',
            username='lskywalker',
            email='lskywalker@gmail.com',
            password='Test123!',
            is_superuser=True
        )
        self.assertNotEqual(self.obj, None)
