#!/usr/bin/python3

from dataclasses import dataclass


def bin_to_hex(*, bin_data: str) -> str:
    """Converts binary to hexadecimal.
    Example bin_to_hex('0b101000011111') returns '0xa1f'.

    :param bin_data: Binary string (type string).
    :return: Hexadecimal representation (type string).
    """

    SCALE = 2
    length = (len(bin_data) - 2) // 4
    hex_data = "0x" + hex(int(bin_data, SCALE))[2:].zfill(length)
    return hex_data


def dec_to_hex(*, dec: int) -> str:
    """Converts the decimal value to Hex representation
    Example dec: 5
    Example return: '0x0005'

    :param dec: Decimal value (type int).
    :return: Hex representation of the decimal value (type string).
    """

    hex_data = "0x" + hex(dec)[2:].zfill(4)
    return hex_data


@dataclass(kw_only=True)
class Hex:
    """ Example hexString property = 0x8c11 """
    hexString: str


    @property
    def hex_to_bin(self) -> str:
        """Converts hexadecimal to binary.
        Example hex_to_bin('0x02') returns '0b00000010'.

        :return: Binary representation (type string).
        """

        SCALE = 16
        bit_length = 4 * (len(self.hexString) - 2)
        bin_data = "0b" + bin(int(self.hexString, SCALE))[2:].zfill(bit_length)
        return bin_data


    @property
    def hex_to_dec(self) -> int:
        """Converts hexadecimal to decimal.
        Example hex_to_dec('0x9e') returns 158.

        :return: Decimal representation (type integer).
        """

        SCALE = 16
        dec_num = int(self.hexString, SCALE)
        return dec_num


    @property
    def checksum(self) -> str:
        """Computes the intel hex checksum value for data integrity verification.
        Example checksum('0x03000000020023') returns '0xd8'.

        :return: Checksum value in hexadecimal (type string).
        """

        record = self.hexString[2:]

        half_record_len = len(record) // 2
        pairs_sum = 0

        for j in range(0, half_record_len):
            pairs_sum += int(record[j*2: j*2+2], 16)

        LSB = pairs_sum % 256
        complement2s_LSB = hex(((LSB ^ 255) + 1) % 256)[2:]

        if len(complement2s_LSB) < 2:
            complement2s_LSB = "0" + complement2s_LSB

        return "0x" + complement2s_LSB


    @property
    def bit_size(self) -> int:
        """Calculates bit length.
        Example bit_length('0xc10') returns 12.

        :return: Bit length (type integer).
        """

        return 4 * (len(self.hexString) - 2)


    @property
    def __repr__(self) -> str:
        """Returns representation of instance of Hex data class.

        :return: Representation of Hex data class instance (type string).
        """

        return (f'{self.__class__.__name__}(hexString={self.hexString})')
