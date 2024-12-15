#!/usr/bin/python3

from dataclasses import dataclass
from typing import List, Dict
from pb224_utilities import Hex, bin_to_hex, dec_to_hex
from digitalpin import DigitalPin
from shifter import Shifter
from record import HexRecord
from termcolor import colored
import threading
import time


def get_lower_addr(l_addr: str) -> str:
    """
    Computes the lower margin address for bulk reading.
    Example l_addr: '0x0002'.
    Example return address: '0x0000'

    :param l_addr: Hexadecimal representation of address (type string).
    :return: lower margin address (type string).
    """

    dec_rep_lower = Hex(hexString=l_addr).hex_to_dec()
    if dec_rep_lower % 8 == 0:
        return l_addr
    else:
        while True:
            dec_rep_lower -= 1
            if dec_rep_lower % 8 == 0:
                return dec_to_hex(dec_rep_lower)


def get_higher_addr(h_addr: str) -> str:
    """
    Computes the higher margin address for bulk reading.
    Example h_addr: '0x0006'
    Example return address: '0x0007'

    :param h_addr: Hexadecimaml representation of address (type string).
    :return: higher margin address (type string).
    """

    dec_rep_higher = Hex(hexString=h_addr).hex_to_dec()
    while True:
        dec_rep_higher += 1
        if dec_rep_higher % 8 == 0:
            return dec_to_hex(dec_rep_higher - 1)


def get_addr_range(start_addr: str, end_addr: str) -> tuple:
    """
    Computes the address space for given addresses.
    Example start_addr: '0x0001'
    Example end_addr: '0x0005'

    :param start_addr: Hexadecimal representation of desired start address (type string).
    :param end_addr: Hexadecimal representation of desired end address (type string).
    return: tuple containing lower and upper address margins (type tuple)
    """

    return (get_lower_addr(start_addr), get_higher_addr(end_addr))


@dataclass(kw_only=True)
class RAM_Interface:
    R_Pins: List[DigitalPin]  # (read_ld, clk, serial_out)
    W_Pins: List[DigitalPin]  # (RI, RI_clk)
    addr_shifter: Shifter
    data_shifter: Shifter


    def read_single_address(self, hex_address: str) -> str:
        """
        Read single address from RAM.
        Example hex_address: '0x3e01'
        Example return data: '0x340024'

        :param hex_address: Hexadecimal representation of address (type string).
        :return: Data from RAM (type string).
        """

        RI, RI_CLK = self.W_Pins
        LD, R_CLK, SER_DATA = self.R_Pins

        # RI disabled
        RI.set_value(value=0)

        # RI_CLK disabled
        # RI_CLK.set_value(value=0)


        # Set address
        self.addr_shifter.shift(shiftHex=Hex(hexString=hex_address))

        time.sleep(0.05)

        # Latch the RAM data in 74HC165
        LD.trigger(transition="0")

        time.sleep(0.05)

        # Shifting out and reading 3 bytes of data
        data_bin_string = "0b"

        data_bin_string += "1" if SER_DATA.read_value() else "0"

        for j in range(23):
            R_CLK.trigger(transition="1")
            time.sleep(0.05)
            data_bin_string += "1" if SER_DATA.read_value() else "0"
            time.sleep(0.05)

        return bin_to_hex(data_bin_string)


    def write_single_address(self, hex_address: str, hex_data: str) -> None:
        """
        Write data to a address.
        Example hex_address: '0x3e01'
        Example hex_data: '0x3400aa'

        :param hex_address: Hex representation of address where data is to be written (type string).
        :param hex_data: Hex representation of data to be written (type string).
        :return: None.
        """

        RI, RI_CLK = self.W_Pins

        # Shifting address and data
        address_shifter_thread = threading.Thread(
            target=self.addr_shifter.shift,
            kwargs={
                'shiftHex': Hex(hexString=hex_address)
            }

        )

        data_shifter_thread = threading.Thread(
            target=self.data_shifter.shift,
            kwargs={
                'shiftHex': Hex(hexString=hex_data)
            }
        )

        address_shifter_thread.start()
        data_shifter_thread.start()
        address_shifter_thread.join()
        data_shifter_thread.join()

        # Writing
        time.sleep(0.05)
        RI.set_value(value=1)
        time.sleep(0.05)
        RI_CLK.trigger(transition="1")
        time.sleep(0.05)
        RI.set_value(value=0)
        time.sleep(0.05)

        print("data written")


    def dump_intel_hexfile(self, record_list: List[HexRecord]) -> Dict[str, str]:
        """
        Writes the machine language in intel hex file to RAM.

        :param record_list: A list of HexRecord objects from the ihex file (type List[HexRecord]).
        :return: Returns back dictionary containing address and corresponding checksum value mappings (type Dict[str:str]).
        """

        # Address and corresponding data checksums for verification
        address_checksum_mappings = {}

        for ihex_record in record_list:
            # Record details
            # byte_count = ihex_record.byte_count()
            addr_field = ihex_record.addr_field()
            # record_type = ihex_record.record_type()
            data_field = ihex_record.data_field()
            checksum = ihex_record.checksum_field()

            self.write_single_address(hex_address=addr_field, hex_data=data_field)
            address_checksum_mappings[addr_field] = checksum
            time.sleep(0.05)

        return address_checksum_mappings


    def bulk_read(self, lower_addr: str, upper_addr: str) -> str:
        """
        Prints the RAM/Memory contents in formatted manner for given address range.
        Example lower_addr: '0x0001'
        Example upper_addr: '0x000a'

        :param lower_addr: The starting address value in hex (type string).
        :param upper_addr: The end address value in hex (type string).
        :return: Returns a string representating RAM/Memory contents in formatted manner (type string)
        """

        desired_range = range(Hex(hexString=lower_addr).hex_to_dec(), Hex(hexString=upper_addr).hex_to_dec() + 1)

        l, u = get_addr_range(lower_addr, upper_addr)
        # print(l, u)
        l_dec = Hex(hexString=l).hex_to_dec()
        u_dec = Hex(hexString=u).hex_to_dec()

        out_string = l[2:] + " " + self.color_inrange(l_dec, desired_range) + " "
        l_dec += 1

        while l_dec <= u_dec:
            if l_dec % 8 == 0:
                out_string += "\n" + dec_to_hex(l_dec)[2:] + " " + self.color_inrange(l_dec, desired_range) + " "
            else:
                out_string += self.color_inrange(l_dec, desired_range) + " "
            l_dec += 1

        return out_string


    def color_inrange(self, counter: int, des_range: range):
        """
        Colors the string in red.

        :param counter: An integer value (type int).
        :param des_range: An range object (type range).
        :return: Colored data value from RAM if the corresponding address in desired address space.
        """

        hex_addr = dec_to_hex(counter)
        data = self.read_single_address(hex_address=hex_addr)
        return colored(data, "red") if counter in des_range else data


    def verify_checksum(self, addr_checksum_mappings: Dict[str, str], byte_count: str, record_type: str) -> None:
        """
        Verifies the checksum for addresses passed.

        :param addr_checksum_mappings: A dictionary containing address and corressponding checksum to be verified (type Dict[str:str]).
        :param byte_count: Byte count of data in hex (type string).
        :param record_type: Record type in hex (type string).
        :retrun: None.
        """

        checksum_verified_status = []

        for addr, checksum in addr_checksum_mappings.items():
            data = self.read_single_address(hex_address=addr)
            read_record_without_checksum_string = "0x" + byte_count[2:] + addr[2:] + record_type[2:] + data[2:]
            read_record_checksum = Hex(hexString=read_record_without_checksum_string).compute_checksum()

            checksum_verified = checksum == read_record_checksum
            checksum_verified_status.append(checksum_verified)

            if checksum_verified:
                print(f"Checksum verified for address: {addr}")
            else:
                print(f"Checksum verification failed for address: {addr}")

        print(all(checksum_verified_status))



    def clear_addr_reg(self) -> None:
        """
        Clears the address shifter.

        :return: None.
        """

        self.addr_shifter.clear_register()


    def clear_data_reg(self) -> None:
        """
        Clears the data shifter.

        :return: None.
        """

        self.data_shifter.clear_register()

    def __repr__(self) -> str:
        """
        Returns representation of instance of RAM_Interface data class.

        :return: Representation of RAM_Interface class instance (type string).
        """

        return (f'{self.__class__.__name__}(R_Pins={self.R_Pins}, W_Pins={self.W_Pins}, addr_shifter={self.addr_shifter}, data_shifter={self.data_shifter})')
