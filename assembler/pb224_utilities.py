#!/usr/bin/python3

from dataclasses import dataclass


def bin_to_hex(bin_data: str) -> str:
    """ Example bin_to_hex('0b101000011111') returns '0xa1f' """
    scale = 2
    length = (len(bin_data) - 2) // 4
    hex_data = "0x" + hex(int(bin_data, scale))[2:].zfill(length)
    return hex_data


@dataclass(kw_only=True)
class Hex:
    """ Example hexString property = 0x8c11 """
    hexString: str


    def hex_to_bin(self) -> str:
        """ Example hex_to_bin('0x02') returns '0b00000010' """
        scale = 16
        bit_length = 4 * (len(self.hexString) - 2)
        bin_data = "0b" + bin(int(self.hexString, scale))[2:].zfill(bit_length)
        return bin_data


    def hex_to_dec(self) -> int:
        """ Example hex_to_dec('0x9e') returns 158 """
        scale = 16
        dec_num = int(self.hexString, scale)
        return dec_num


    def compute_checksum(self) -> str:
        """ Example compute_checksum('0x03000000020023') returns '0xd8' """
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


    def bit_size(self) -> int:
        """ Example bit_length('0xc10') returns 12 """
        return 4 * (len(self.hexString) - 2)

