from csv import DictReader
from dataclasses import dataclass
from typing import Dict, List, Type, TextIO

from django.db import transaction
from rest_framework.serializers import Serializer


class InvalidBulkUpdate(Exception):
    """
    Exception indicating that the bulk adding failed
    """
    def __init__(self, error):
        super().__init__()
        self.error = error


@dataclass
class AddBulkConfig:
    """
    Configuration for bulk adding
    """
    serializer: Type[Serializer]
    format: str
    mapping: Dict[str, str]


def add_bulk_from_file(file_data: TextIO, config: AddBulkConfig) -> List[int]:
    """
    Add all the elements defined in the file_data according to the
    given configuration
    Supported formats: csv

    :param file_data: Sequence of lines containing the events
    :param config: Configuration that should be used for the adding
    :return: The ids of the added events
    """

    if config.format == "csv":
        return _add_bulk_from_csv(file_data, config)

    raise InvalidBulkUpdate(f"Unknown file type {config.format}")


def _add_bulk_from_csv(file_data: TextIO, config: AddBulkConfig) -> List[int]:
    """
    Add all the elements defined in the csv file represented by file_data,
    according to the given configuration

    :param file_data: Sequence of lines containing the events
    :param config: Configuration that should be used for the adding
    :return: The ids of the added events
    """

    reader = DictReader(file_data)
    _check_csv_keys(reader, config)

    ids = []
    with transaction.atomic():
        for i, data in enumerate(reader, 2):
            if config.mapping:
                data = {
                    config.mapping[key]: value
                    for key, value in data.items()
                    if key in config.mapping
                }

            serializer = config.serializer(data=data)
            if not serializer.is_valid():
                raise InvalidBulkUpdate(
                    f"The following error happened during deserialization "
                    f"of line {i} of the csv file: {serializer.errors}"
                )
            element = serializer.save()
            ids.append(element.id)

    return ids


def _check_csv_keys(reader: DictReader, config: AddBulkConfig):
    """
    Ensure that the given csv file can be used to create the desired objects
    by checking that the required keys are available

    :param reader: CSV dictionary reader that wraps the file
    :param config: Post bulk configuration
    :raise: InvalidBulkUpdate if the csv file cannot be used
    """

    required_keys = set(config.serializer().fields)
    # id nor url are required for the creation of an element
    required_keys.remove("id")

    if "url" in required_keys:
        required_keys.remove("url")

    if config.mapping:
        missing_keys = required_keys.difference(config.mapping.values())
        if missing_keys:
            raise InvalidBulkUpdate(
                "The following target field are missing from the mapping "
                f"to be able to create the objects: {missing_keys}"
            )
    else:
        missing_keys = required_keys.difference(reader.fieldnames)
        if missing_keys:
            raise InvalidBulkUpdate(
                "The following field are missing from the given csv file"
                f"to be able to create the objects: {missing_keys}"
            )

    missing_keys = set(config.mapping).difference(reader.fieldnames)
    if missing_keys:
        raise InvalidBulkUpdate(
            "The following source field that were given for mapping are not "
            f"available in the header of the given csv file: {missing_keys}"
        )
