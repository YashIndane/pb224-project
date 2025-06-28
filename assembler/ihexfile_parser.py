#!/usr/bin/python3

from record import HexRecord
from typing import List


def parse_intel_hexfile(*, filename: str) -> List[HexRecord]:
    """
    Parse the given ihex file.

    :param filename: Path of ihex file (type string).
    :return: Returns list of HexRecord objects (type List[HexRecord]).
    """

    _dump_hex_records = []

    with open(file=filename, mode="r") as _ihexfile:
        _data = _ihexfile.read()
        for _record in _data.split("\n"):
            _dump_hex_records.append(
                HexRecord(_record)
            )
        _ihexfile.close()

    # Remove last element from list
    _dump_hex_records.pop()

    return _dump_hex_records
