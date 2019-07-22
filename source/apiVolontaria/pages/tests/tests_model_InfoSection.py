from rest_framework.test import APITransactionTestCase

from ..models import InfoSection


class InfoSectionTests(APITransactionTestCase):

    def setUp(self):
        pass

    def test_create_info_section(self):
        """
        Ensure we can create a new InfoSection
        """
        info_section = InfoSection.objects.create(
            is_active=True,
            title='My title',
            content='My Content',
        )

        self.assertEqual(info_section.title, 'My title')
        self.assertEqual(info_section.content, 'My Content')
