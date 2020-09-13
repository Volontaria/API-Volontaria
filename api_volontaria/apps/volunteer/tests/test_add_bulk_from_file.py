from io import StringIO

from django.test import TestCase

from api_volontaria.apps.volunteer.helpers import (
    InvalidBulkUpdate,
    add_bulk_from_file,
    AddBulkConfig
)
from api_volontaria.apps.volunteer.models import TaskType
from api_volontaria.apps.volunteer.serializers import TaskTypeSerializer

TASK_TYPE_VALID_CSV_HEADER = "name,"
TASK_TYPE_INVALID_CSV_HEADER = "name_typo,"
TASK_TYPE_CUSTOM_CSV_HEADER = "name_custom,"

TASK_TYPE_VALID_CSV_LINE = "take_type_name,"
# Invalid because of name other a 100 characters
TASK_TYPE_INVALID_CSV_LINE = "abcdefj" * 100 + ","

TASK_TYPE_VALID_CUSTOM_MAPPING = {"name_custom": "name"}
TASK_TYPE_CUSTOM_MAPPING_MISSING_HEADER_KEY = {"name_custom_typo": "name"}
TASK_TYPE_CUSTOM_MAPPING_MISSING_TARGET_KEY = {
    "name_typo": "name_will_be_missing"
}


def make_file_data(*lines: str):
    return StringIO("\n".join(lines))


class TestAddBulk(TestCase):
    def test_unknown_format_is_given(self):
        """
        Ensure an InvalidBulkUpdate exception is raised
        when an unknown format is given
        """
        self.assertRaises(
            InvalidBulkUpdate,
            add_bulk_from_file,
            make_file_data(),
            AddBulkConfig(TaskTypeSerializer, "abc", {})
        )

    def test_csv_header_is_missing_required_fields(self):
        """
        Ensure an InvalidBulkUpdate exception is raised
        when the csv header is missing keys for the
        creation of the requested elements
        """
        self.assertRaises(
            InvalidBulkUpdate,
            add_bulk_from_file,
            make_file_data(TASK_TYPE_INVALID_CSV_HEADER),
            AddBulkConfig(TaskTypeSerializer, "csv", {})
        )

    def test_mapping_key_is_not_present_in_csv_header(self):
        """
        Ensure an InvalidBulkUpdate exception is raised
        when the given mapping has a key which is not
        present in the csv header
        """
        file_data = make_file_data(
            TASK_TYPE_CUSTOM_CSV_HEADER,
            TASK_TYPE_VALID_CSV_LINE
        )
        config = AddBulkConfig(
            TaskTypeSerializer,
            "csv",
            TASK_TYPE_CUSTOM_MAPPING_MISSING_HEADER_KEY
        )

        self.assertRaises(
            InvalidBulkUpdate,
            add_bulk_from_file,
            file_data,
            config
        )

    def test_required_key_is_not_in_custom_mapping_values(self):
        """
        Ensure an InvalidBulkUpdate exception is raised
        when the given mapping does not have all the required
        keys in its values
        """
        file_data = make_file_data(
            TASK_TYPE_CUSTOM_CSV_HEADER,
            TASK_TYPE_VALID_CSV_LINE
        )
        config = AddBulkConfig(
            TaskTypeSerializer,
            "csv",
            TASK_TYPE_CUSTOM_MAPPING_MISSING_TARGET_KEY
        )

        self.assertRaises(
            InvalidBulkUpdate,
            add_bulk_from_file,
            file_data,
            config
        )

    def test_unserializable_entry(self):
        """
        Ensure that no element is added (even the valid ones) if any
        of the elements is invalid
        """
        initial_number = TaskType.objects.count()

        # The first 4 lines are valid and only the 5 one
        # should make the function throw an exception
        file_data = make_file_data(
            TASK_TYPE_VALID_CSV_HEADER,
            TASK_TYPE_VALID_CSV_LINE,
            TASK_TYPE_VALID_CSV_LINE,
            TASK_TYPE_VALID_CSV_LINE,
            TASK_TYPE_INVALID_CSV_LINE,
            TASK_TYPE_VALID_CSV_LINE,
        )

        self.assertRaises(
            InvalidBulkUpdate,
            add_bulk_from_file,
            file_data,
            AddBulkConfig(TaskTypeSerializer, "csv", {})
        )
        self.assertEqual(initial_number, TaskType.objects.count())

    def test_nominal_case_elements_are_added_and_ids_are_returned(self):
        """
        Ensure that a successful bulk operation adds the elements
        to the database and returns the created ids
        """
        file_data = make_file_data(
            TASK_TYPE_VALID_CSV_HEADER,
            TASK_TYPE_VALID_CSV_LINE,
            TASK_TYPE_VALID_CSV_LINE
        )
        config = AddBulkConfig(TaskTypeSerializer, "csv", {})

        initial_number = TaskType.objects.count()
        initial_list = list(TaskType.objects.values_list('id', flat=True))

        ids = add_bulk_from_file(file_data, config)

        final_ids = set(TaskType.objects.values_list('id', flat=True))
        created_ids = final_ids.difference(initial_list)

        self.assertSetEqual(created_ids, set(ids))
        self.assertEqual(initial_number + 2, TaskType.objects.count())

    def test_mapping_case_elements_are_added_and_values_are_returned(self):
        """
        Ensure that a successful bulk operation with mapping adds
        the elements to the database and returns the created ids
        """
        file_data = make_file_data(
            TASK_TYPE_CUSTOM_CSV_HEADER,
            TASK_TYPE_VALID_CSV_LINE,
            TASK_TYPE_VALID_CSV_LINE
        )
        config = AddBulkConfig(
            TaskTypeSerializer,
            "csv",
            TASK_TYPE_VALID_CUSTOM_MAPPING
        )

        initial_number = TaskType.objects.count()
        initial_list = list(TaskType.objects.values_list('id', flat=True))

        ids = add_bulk_from_file(file_data, config)

        final_ids = set(TaskType.objects.values_list('id', flat=True))
        created_ids = final_ids.difference(initial_list)

        self.assertSetEqual(created_ids, set(ids))
        self.assertEqual(initial_number + 2, TaskType.objects.count())
