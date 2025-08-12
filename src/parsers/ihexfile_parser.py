#!/usr/bin/python3

"""Module to parse the IntelHex File"""

from __future__ import annotations

from src.utilities.record import HexRecord
from typing import List


def parse_intel_hexfile(*, filename: str) -> List[HexRecord]:
    """Parse the given ihex file.

    :param filename: Path of ihex file (type string).
    :return: Returns list of HexRecord objects (type List[HexRecord]).
    """

    dump_hex_records = []

    with open(file=filename, mode="r") as ihexfile:
        data = ihexfile.read()
        for record in data.split("\n"):
            dump_hex_records.append(
                HexRecord(record)
            )
        ihexfile.close()

    # Remove last element from list
    dump_hex_records.pop()

    return dump_hex_records
