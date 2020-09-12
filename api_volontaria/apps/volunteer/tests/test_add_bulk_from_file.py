from io import StringIO

from django.test import TestCase

from api_volontaria.apps.volunteer.helpers import InvalidBulkUpdate, add_bulk_from_file, AddBulkConfig
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
TASK_TYPE_CUSTOM_MAPPING_MISSING_TARGET_KEY = {"name_typo": "name_will_be_missing"}


def make_file_data(*lines: str):
    return StringIO("\n".join(lines))


class TestAddBulk(TestCase):
    def test_should_throw_exception_when_unknown_format_is_given(self):
        self.assertRaises(
            InvalidBulkUpdate,
            add_bulk_from_file,
            make_file_data(),
            AddBulkConfig(TaskTypeSerializer, "abc", {})
        )

    def test_should_throw_exception_when_header_is_missing_required_fields(self):
        self.assertRaises(
            InvalidBulkUpdate,
            add_bulk_from_file,
            make_file_data(TASK_TYPE_INVALID_CSV_HEADER),
            AddBulkConfig(TaskTypeSerializer, "csv", {})
        )

    def test_should_throw_exception_when_custom_mapping_key_is_not_present_in_csv_header(self):
        self.assertRaises(
            InvalidBulkUpdate,
            add_bulk_from_file,
            make_file_data(TASK_TYPE_CUSTOM_CSV_HEADER, TASK_TYPE_VALID_CSV_LINE),
            AddBulkConfig(TaskTypeSerializer, "csv", TASK_TYPE_CUSTOM_MAPPING_MISSING_HEADER_KEY)
        )

    def test_should_throw_exception_when_required_key_is_not_in_custom_mapping_values(self):
        self.assertRaises(
            InvalidBulkUpdate,
            add_bulk_from_file,
            make_file_data(TASK_TYPE_CUSTOM_CSV_HEADER, TASK_TYPE_VALID_CSV_LINE),
            AddBulkConfig(TaskTypeSerializer, "csv", TASK_TYPE_CUSTOM_MAPPING_MISSING_TARGET_KEY)
        )

    def test_should_throw_exception_when_serializer_detect_invalid_entry(self):
        initial_number = TaskType.objects.count()

        self.assertRaises(
            InvalidBulkUpdate,
            add_bulk_from_file,
            make_file_data(TASK_TYPE_VALID_CSV_HEADER, TASK_TYPE_INVALID_CSV_LINE),
            AddBulkConfig(TaskTypeSerializer, "csv", {})
        )
        assert initial_number == TaskType.objects.count()

    def test_should_not_add_any_element_if_an_element_is_invalid(self):
        initial_number = TaskType.objects.count()

        # The first 4 lines are valid and only the 5 one should make the function throw an exception
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
        assert initial_number == TaskType.objects.count()

    def test_nominal_case_the_elements_are_added_and_values_are_returned(self):
        file_data = make_file_data(
            TASK_TYPE_VALID_CSV_HEADER, TASK_TYPE_VALID_CSV_LINE, TASK_TYPE_VALID_CSV_LINE
        )
        config = AddBulkConfig(TaskTypeSerializer, "csv", {})

        initial_number = TaskType.objects.count()

        ids = add_bulk_from_file(file_data, config)

        assert len(ids) == 2
        assert initial_number + 2 == TaskType.objects.count()

    def test_nominal_case_custom_mapping_the_elements_are_added_and_values_are_returned(self):
        file_data = make_file_data(
            TASK_TYPE_CUSTOM_CSV_HEADER, TASK_TYPE_VALID_CSV_LINE, TASK_TYPE_VALID_CSV_LINE
        )
        config = AddBulkConfig(TaskTypeSerializer, "csv", TASK_TYPE_VALID_CUSTOM_MAPPING)

        initial_number = TaskType.objects.count()

        ids = add_bulk_from_file(file_data, config)

        assert len(ids) == 2
        assert initial_number + 2 == TaskType.objects.count()
