from rest_framework.test import APITestCase


from rest_framework.test import APITestCase


class CustomAPITestCase(APITestCase):
    ATTRIBUTES = []

    def check_attributes(self, content, attrs=None):
        if attrs is None:
            attrs = self.ATTRIBUTES

        missing_keys = list(set(attrs) - set(content.keys()))
        extra_keys = list(set(content.keys()) - set(attrs))
        self.assertEqual(
            len(missing_keys),
            0,
            'You miss some attributes: ' + str(missing_keys)
        )
        self.assertEqual(
            len(extra_keys),
            0,
            'You have some extra attributes: ' + str(extra_keys)
        )
