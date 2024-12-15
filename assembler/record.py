#!/usr/bin/python3

from dataclasses import dataclass, field


@dataclass
class HexRecord:
    record_string: str

    def byte_count(self) -> str:
        """
        Byte count of data in hex

        :return: Returns byte count of data (type string).
        """

        return "0x" + self.record_string[1:3]


    def addr_field(self) -> str:
        """
        Address field of the record in hex.

        :return: Returns address of record (type string).
        """

        return "0x" + self.record_string[3:7]


    def record_type(self) -> str:
        """
        Record type of record in hex.

        :return: Returns record type of record (type string).
        """

        return "0x" + self.record_string[7:9]


    def data_field(self) -> str:
        """
        Data field of record type in hex.

        :return: Returns data field of record (type string).
        """

        return "0x" + self.record_string[9:15]


    def checksum_field(self) -> str:
        """
        Checksum field of record in hex.

        :return: Returns checksum field of record (type string).
        """

        return "0x" + self.record_string[15:17]


    def __repr__(self) -> str:
        """
        Representation of instance of HexRecord class.

        :return: Returns representation of instance of HexRecord class (type string).
        """

        return (f'{self.__class__.__name__}(record_string={self.record_string})')
