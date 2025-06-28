#!/usr/bin/python3

from dataclasses import dataclass
from typing import List, Dict
from pb224_utilities import Hex, bin_to_hex, dec_to_hex
from digitalpin import DigitalPin
from shifter import Shifter
from record import HexRecord
from termcolor import colored
from tqdm import tqdm
import threading
import time


def checksum_status_pbar(func):
    """
    Status bar decorator for checksum verification.
    """
    def wrapper(otherSelf, **kwargs) -> str:
        _addr_check_mappings = kwargs["addr_checksum_mappings"]
        _byte_c = kwargs["byte_count"]
        _record_type = kwargs["record_type"]

        with tqdm(total=len(_addr_check_mappings), desc="Checksum Verification Status") as _pbar:
            _checksum_status_log = func(self=otherSelf,
                                        addr_checksum_mappings=_addr_check_mappings,
                                        byte_count=_byte_c,
                                        record_type=_record_type,
                                        progress_bar=_pbar
                                   )
        return _checksum_status_log
    return wrapper


def bulk_read_status_pbar(func):
    """
    Status bar decorator for RAM Bulk Reading.
    """
    def wrapper(otherSelf, **kwargs) -> str:
        _l_addr = kwargs["lower_addr"]
        _u_addr = kwargs["upper_addr"]
        _l, _u = RAM_Interface.get_addr_range(start_addr=_l_addr, end_addr=_u_addr)
        with tqdm(total=(Hex(hexString=_u).hex_to_dec() - Hex(hexString=_l).hex_to_dec() + 1), desc="Bulk Read Status") as _pbar:
            _bulk_read_status_log = func(self=otherSelf,
                                         lower_addr=_l_addr,
                                         upper_addr=_u_addr,
                                         progress_bar=_pbar
                                    )
        return _bulk_read_status_log
    return wrapper


def dump_intel_hexfile_pbar(func):
    """
    Status bar decorator for Intel Hex File Dump.
    """
    def wrapper(otherSelf, **kwargs):
        _record_list = kwargs["record_list"]
        with tqdm(total=len(_record_list), desc="Dumping Intel Hex File") as _pbar:
            _dump_log = func(self=otherSelf,
                             record_list=_record_list,
                             progress_bar=_pbar
                        )
        return _dump_log
    return wrapper



@dataclass(kw_only=True)
class RAM_Interface:
    R_Pins: List[DigitalPin]  # (read_ld, clk, serial_out)
    W_Pins: List[DigitalPin]  # (RI, RI_clk)
    addr_shifter: Shifter
    data_shifter: Shifter
    checksum_notifier: DigitalPin


    @staticmethod
    def get_lower_addr(*, l_addr: str) -> str:
        """
        Computes the lower margin address for bulk reading.
        Example l_addr: '0x0002'
        Example return address: '0x0000'

        :param l_addr: Hexadecimal representation of address (type string).
        :return: lower margin address (type string).
        """

        _dec_rep_lower = Hex(hexString=l_addr).hex_to_dec()
        if _dec_rep_lower % 8 == 0:
            return l_addr
        else:
            while True:
                _dec_rep_lower -= 1
                if _dec_rep_lower % 8 == 0:
                    return dec_to_hex(_dec_rep_lower)


    @staticmethod
    def get_higher_addr(*, h_addr: str) -> str:
        """
        Computes the higher margin address for bulk reading.
        Example h_addr: '0x0006'
        Example retrun address: '0x0007'

        :param h_addr: Hexadecimal representation of address (type string).
        :return: higher margin address (type string).
        """

        _dec_rep_higher = Hex(hexString=h_addr).hex_to_dec()
        while True:
            _dec_rep_higher += 1
            if _dec_rep_higher % 8 == 0:
                return dec_to_hex(_dec_rep_higher - 1)


    @staticmethod
    def get_addr_range(*, start_addr: str, end_addr: str) -> tuple:
        """
        Computes the address space for given addresses.
        Example start_addr: '0x0001'
        Example end_addr: '0x0005'

        :param start_addr: Hexadecimal representation of desired start address (type string).
        :param end_addr: Hexadecimal representation of desired end address (type string).
        return: tuple containing lower and upper address margins (type tuple).

        """

        return (RAM_Interface.get_lower_addr(l_addr=start_addr), RAM_Interface.get_higher_addr(h_addr=end_addr))



    def read_single_address(self, hex_address: str) -> str:
        """
        Read single address from RAM.
        Example hex_address: '0x3e01'
        Example return data: '0x340024'

        :param hex_address: Hexadecimal representation of address (type string).
        :return: Data from RAM (type string).
        """

        _RI, _RI_CLK = self.W_Pins
        _LD, _R_CLK, _SER_DATA = self.R_Pins

        # RI disabled
        _RI.set_value(value=0)

        # RI_CLK disabled
        # RI_CLK.set_value(value=0)


        # Set address
        self.addr_shifter.shift(shiftHex=Hex(hexString=hex_address))

        time.sleep(0.05)

        # Latch the RAM data in 74HC165
        _LD.trigger(transition="0")

        time.sleep(0.05)

        # Shifting out and reading 3 bytes of data
        _data_bin_string = "0b"

        _data_bin_string += "1" if _SER_DATA.read_value() else "0"

        for _ in range(23):
            _R_CLK.trigger(transition="1")
            time.sleep(0.05)
            _data_bin_string += "1" if _SER_DATA.read_value() else "0"
            time.sleep(0.05)

        return bin_to_hex(_data_bin_string)


    def write_single_address(self, hex_address: str, hex_data: str) -> None:
        """
        Write data to a address.
        Example hex_address: '0x3e01'
        Example hex_data: '0x3400aa'

        :param hex_address: Hex representation of address where data is to be written (type string).
        :param hex_data: Hex representation of data to be written (type string).
        :return: None.
        """

        _RI, _RI_CLK = self.W_Pins

        # Shifting address and data
        _address_shifter_thread = threading.Thread(
            target=self.addr_shifter.shift,
            kwargs={
                'shiftHex': Hex(hexString=hex_address)
            }

        )

        _data_shifter_thread = threading.Thread(
            target=self.data_shifter.shift,
            kwargs={
                'shiftHex': Hex(hexString=hex_data)
            }
        )

        _address_shifter_thread.start()
        _data_shifter_thread.start()
        _address_shifter_thread.join()
        _data_shifter_thread.join()

        # Writing
        time.sleep(0.05)
        _RI.set_value(value=1)
        time.sleep(0.05)
        _RI_CLK.trigger(transition="1")
        time.sleep(0.05)
        _RI.set_value(value=0)
        time.sleep(0.05)

        #print("data written")


    @dump_intel_hexfile_pbar
    def dump_intel_hexfile(self, record_list: List[HexRecord], progress_bar=None) -> Dict[str, str]:
        """
        Writes the machine language in intel hex file to RAM.

        :param record_list: A list of HexRecord objects from the ihex file (type List[HexRecord]).
        :return: Returns back dictionary containing address and corresponding checksum value mappings (type Dict[str:str]).
        """

        # Address and corresponding data checksums for verification
        _address_checksum_mappings = {}

        for _ihex_record in record_list:
            # Record details
            # byte_count = ihex_record.byte_count()
            _addr_field = _ihex_record.addr_field()
            # record_type = ihex_record.record_type()
            _data_field = _ihex_record.data_field()
            _checksum = _ihex_record.checksum_field()

            self.write_single_address(hex_address=_addr_field, hex_data=_data_field)
            _address_checksum_mappings[_addr_field] = _checksum
            time.sleep(0.05)

            progress_bar.update(1)

        return _address_checksum_mappings


    @bulk_read_status_pbar
    def bulk_read(self, lower_addr: str, upper_addr: str, progress_bar=None) -> str:
        """
        Prints the RAM/Memory contents in formatted manner for given address range.
        Example lower_addr: '0x0001'
        Example upper_addr: '0x000a'

        :param lower_addr: The starting address value in hex (type string).
        :param upper_addr: The end address value in hex (type string).
        :return: Returns a string representating RAM/Memory contents in formatted manner (type string)
        """

        _desired_range = range(Hex(hexString=lower_addr).hex_to_dec(), Hex(hexString=upper_addr).hex_to_dec() + 1)

        _l, _u = RAM_Interface.get_addr_range(start_addr=lower_addr, end_addr=upper_addr)
        # print(l, u)
        _l_dec = Hex(hexString=_l).hex_to_dec()
        _u_dec = Hex(hexString=_u).hex_to_dec()

        _out_string = _l[2:] + " " + self.color_inrange(_l_dec, _desired_range) + " "
        _l_dec += 1

        while _l_dec <= _u_dec:
            if _l_dec % 8 == 0:
                _out_string += "\n" + dec_to_hex(_l_dec)[2:] + " " + self.color_inrange(_l_dec, _desired_range) + " "
            else:
                _out_string += self.color_inrange(_l_dec, _desired_range) + " "
            _l_dec += 1

            progress_bar.update(1)

        return _out_string


    def color_inrange(self, counter: int, des_range: range):
        """
        Colors the string in red.

        :param counter: An integer value (type int).
        :param des_range: An range object (type range).
        :return: Colored data value from RAM if the corresponding address in desired address space.
        """

        _hex_addr = dec_to_hex(counter)
        _data = self.read_single_address(hex_address=_hex_addr)
        return colored(_data, "red") if counter in des_range else _data


    @checksum_status_pbar
    def verify_checksum(self, addr_checksum_mappings: Dict[str, str], byte_count: str, record_type: str, progress_bar=None) -> None:
        """
        Verifies the checksum for addresses passed.

        :param addr_checksum_mappings: A dictionary containing address and corressponding checksum to be verified (type Dict[str:str]).
        :param byte_count: Byte count of data in hex (type string).
        :param record_type: Record type in hex (type string).
        :retrun: None.
        """

        _checksum_verified_status = []
        _checksum_status_log = ""

        for _addr, _checksum in addr_checksum_mappings.items():
            _data = self.read_single_address(hex_address=_addr)
            _read_record_without_checksum_string = "0x" + byte_count[2:] + _addr[2:] + record_type[2:] + _data[2:]
            _read_record_checksum = Hex(hexString=_read_record_without_checksum_string).compute_checksum()

            _checksum_verified = _checksum == _read_record_checksum
            _checksum_verified_status.append(_checksum_verified)

            if _checksum_verified:
                _checksum_status_log += f"Checksum verified for address: {_addr}\n"
            else:
                _checksum_status_log += f"Checksum verification failed for address: {_addr}\n"

            progress_bar.update(1)

        if all(_checksum_verified_status):
            self.checksum_notifier.set_value(1)
            time.sleep(0.5)
            self.checksum_notifier.set_value(0)
            time.sleep(0.5)
            self.checksum_notifier.set_value(1)
            time.sleep(0.5)
            self.checksum_notifier.set_value(0)
            time.sleep(0.5)

        return _checksum_status_log



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
