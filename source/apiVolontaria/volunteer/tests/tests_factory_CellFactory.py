from rest_framework.test import APITransactionTestCase

from location.factories import AddressFactory
from ..factories import CellFactory


class CellFactoryTests(APITransactionTestCase):

    def setUp(self):
        pass

    def test_create_cell_object(self):
        self.obj = CellFactory()
        self.assertNotEqual(self.obj, None)

    def test_create_cell_with_name(self):
        self.obj = CellFactory(name='New Cell')
        self.assertNotEqual(self.obj, None)
        self.assertNotEqual(self.obj.__str__(), None)

    def test_create_cell_with_params(self):
        address = AddressFactory()
        self.obj = CellFactory(name='New Cell', address=address)
        self.assertNotEqual(self.obj, None)
