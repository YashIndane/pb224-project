#!/usr/bin/python3

"""Module to manage the RAM

PB224 RAM consists of 3 [MS62256A-20NC] 32K*8 High Speed CMOS Static RAMs
which act as the main memory for this CPU.
"""

from __future__ import annotations

import threading
import logging
import time

from typing import (
    List,
    Dict,
    Tuple,
    Union,
    ContextManager,
    Callable,
    Optional,
)

from src.utilities.pb224_utilities import Hex, bin_to_hex, dec_to_hex
from src.entities.digitalpin import DigitalPin
from src.entities.shifter import Shifter
from src.utilities.record import HexRecord
from dataclasses import dataclass
from termcolor import colored
from tqdm import tqdm


logger = logging.getLogger(__name__)


def checksum_status_pbar(func) -> Callable[..., str]:
    """Status bar decorator for checksum verification."""

    def wrapper(otherSelf, **kwargs) -> str:
        addr_check_mappings = kwargs["addr_checksum_mappings"]

        with tqdm(
            total=len(addr_check_mappings), desc="Checksum Verification Status"
        ) as pbar:
            kwargs["progress_bar"] = pbar
            checksum_status_log = func(
                otherSelf,
                **kwargs,
            )
        return checksum_status_log
    return wrapper


def bulk_read_status_pbar(func) -> Callable[..., str]:
    """Status bar decorator for RAM Bulk Reading."""

    def wrapper(otherSelf, **kwargs) -> str:
        l_addr = kwargs["lower_addr"]
        u_addr = kwargs["upper_addr"]

        l, u = RAM_Interface._get_addr_range(
            start_addr=l_addr,
            end_addr=u_addr,
        )

        with tqdm(
            total=(Hex(hexString=u).hex_to_dec - Hex(hexString=l).hex_to_dec + 1),
            desc="Bulk Read Status",
        ) as pbar:
            kwargs["progress_bar"] = pbar
            bulk_read_status_log = func(
                otherSelf,
                **kwargs,
            )
        return bulk_read_status_log
    return wrapper


def dump_intel_hexfile_pbar(func) -> Callable[..., Dict[str, str]]:
    """Status bar decorator for Intel Hex File Dump."""

    def wrapper(otherSelf, **kwargs) -> Dict[str, str]:
        record_list = kwargs["record_list"]
        with tqdm(total=len(record_list), desc="Dumping Intel Hex File") as pbar:
            kwargs["progress_bar"] = pbar
            dump_log = func(
                otherSelf,
                **kwargs,
            )
        return dump_log
    return wrapper


@dataclass(kw_only=True)
class RAM_Interface:
    R_Pins: List[DigitalPin]  # (read_ld, clk, serial_out)
    W_Pins: List[DigitalPin]  # (RI, RI_clk)
    addr_shifter: Shifter
    data_shifter: Shifter
    checksum_notifier: DigitalPin


    @staticmethod
    def _get_lower_addr(*, l_addr: str) -> str:
        """Computes the lower margin address for bulk reading.
        Example l_addr: '0x0002'
        Example return address: '0x0000'

        :param l_addr: Hexadecimal representation of address (type string).
        :return: lower margin address (type string).
        """

        dec_rep_lower = Hex(hexString=l_addr).hex_to_dec
        if dec_rep_lower % 8 == 0:
            return l_addr
        else:
            while True:
                dec_rep_lower -= 1
                if dec_rep_lower % 8 == 0:
                    return dec_to_hex(dec=dec_rep_lower)


    @staticmethod
    def _get_higher_addr(*, h_addr: str) -> str:
        """Computes the higher margin address for bulk reading.
        Example h_addr: '0x0006'
        Example retrun address: '0x0007'

        :param h_addr: Hexadecimal representation of address (type string).
        :return: higher margin address (type string).
        """

        dec_rep_higher = Hex(hexString=h_addr).hex_to_dec
        while True:
            dec_rep_higher += 1
            if dec_rep_higher % 8 == 0:
                return dec_to_hex(dec=dec_rep_higher - 1)


    @staticmethod
    def _get_addr_range(*, start_addr: str, end_addr: str) -> Tuple[str, str]:
        """Computes the address space for given addresses.
        Example start_addr: '0x0001'
        Example end_addr: '0x0005'

        :param start_addr: Hexadecimal representation of desired start address (type string).
        :param end_addr: Hexadecimal representation of desired end address (type string).
        return: tuple containing lower and upper address margins (type tuple).
        """

        return (
            RAM_Interface._get_lower_addr(l_addr=start_addr),
            RAM_Interface._get_higher_addr(h_addr=end_addr),
        )


    def read_single_address(self, *, hex_address: str) -> str:
        """Read single address from RAM.
        Example hex_address: '0x3e01'
        Example return data: '0x340024'

        :param hex_address: Hexadecimal representation of address (type string).
        :return: Data from RAM (type string).
        """

        RI, RI_CLK = self.W_Pins
        LD, R_CLK, SER_DATA = self.R_Pins

        try:

            # RI disabled
            RI.set_value(value=0)

            # RI_CLK disabled
            # RI_CLK.set_value(value=0)


            # Set address
            self.addr_shifter.shift(shiftHex=Hex(hexString=hex_address))

            time.sleep(.05)

            # Latch the RAM data in 74HC165
            LD.trigger(transition="0")

            time.sleep(.05)

            # Shifting out and reading 3 bytes of data
            data_bin_string = "0b"

            data_bin_string += ("0", "1")[SER_DATA.read_value()]

            for _ in range(23):
                R_CLK.trigger(transition="1")
                time.sleep(.05)
                data_bin_string += ("0", "1")[SER_DATA.read_value()]
                time.sleep(.05)

            #logger.info(colored(f"address read: {hex_address}", "yellow"))
            return bin_to_hex(bin_data=data_bin_string)

        except Exception as e:
            logger.info(e)


    def write_single_address(self, *, hex_address: str, hex_data: str) -> None:
        """Write data to a address.
        Example hex_address: '0x3e01'
        Example hex_data: '0x3400aa'

        :param hex_address: Hex representation of address where data is to be written (type string).
        :param hex_data: Hex representation of data to be written (type string).
        :return: None.
        """

        RI, RI_CLK = self.W_Pins

        # Threads list
        threads_list: list[
            threading.Thread,  # Address shifter thread
            threading.Thread,  # Data shifter thread
        ] = []

        try:
            # Populating threads list
            for inx in range(2):
                threads_list.append(threading
                    .Thread(
                        target=(
                            self.addr_shifter.shift, self.data_shifter.shift
                        )[inx],
                        kwargs={
                            "shiftHex": Hex(
                                hexString=(hex_address, hex_data)[inx]
                            )
                        },
                        name=f"{'address_shifter_thread' if not inx else 'data_shifter_thread'}: {__name__}",
                    )
                )

            # Thread execution for shifting data & address parallelly
            for c in range(2):
                for thread in threads_list:
                    thread.start() if not c else thread.join()

            # Writing
            time.sleep(.05)
            RI.set_value(value=1)
            time.sleep(.05)
            RI_CLK.trigger(transition="1")
            time.sleep(.05)
            RI.set_value(value=0)
            time.sleep(.05)

            #logger.info(colored(f"data written: {hex_address}", "green"))

        except Exception as e:
            logger.error(e)


    @dump_intel_hexfile_pbar
    def dump_intel_hexfile(
        self,
        *,
        record_list: List[HexRecord],
        progress_bar: Union[ContextManager, None]=None,
    ) -> Dict[str, str]:
        """Writes the machine language in intel hex file to RAM.

        :param record_list: A list of HexRecord objects from the ihex file (type List[HexRecord]).
        :return: Returns back dictionary containing address and corresponding checksum value mappings (type Dict[str:str]).
        """

        # Address and corresponding data checksums for verification
        address_checksum_mappings = {}

        for ihex_record in record_list:
            # Record details
            # byte_count = ihex_record.byte_count()
            addr_field = ihex_record.addr_field
            # record_type = ihex_record.record_type()
            data_field = ihex_record.data_field
            checksum = ihex_record.checksum_field

            self.write_single_address(hex_address=addr_field, hex_data=data_field)
            address_checksum_mappings[addr_field] = checksum
            time.sleep(.05)

            progress_bar.update(1)

        logger.info(colored("INTEL HEX FILE DUMP SUCCESSFUL", "blue"))
        return address_checksum_mappings


    @bulk_read_status_pbar
    def bulk_read(
        self,
        *,
        lower_addr: str,
        upper_addr: str,
        progress_bar: Union[ContextManager, None]=None,
    ) -> str:
        """Prints the RAM/Memory contents in formatted manner for given address range.
        Example lower_addr: '0x0001'
        Example upper_addr: '0x000a'

        :param lower_addr: The starting address value in hex (type string).
        :param upper_addr: The end address value in hex (type string).
        :return: Returns a string representating RAM/Memory contents in formatted manner (type string)
        """

        desired_range = range(
            Hex(hexString=lower_addr).hex_to_dec, Hex(hexString=upper_addr).hex_to_dec + 1
        )

        l, u = RAM_Interface._get_addr_range(start_addr=lower_addr, end_addr=upper_addr)
        # print(l, u)
        l_dec = Hex(hexString=l).hex_to_dec
        u_dec = Hex(hexString=u).hex_to_dec

        out_string = l[2:] + " " + self.color_inrange(counter=l_dec, des_range=desired_range) + " "
        l_dec += 1
        progress_bar.update(1)

        while l_dec <= u_dec:
            if l_dec % 8 == 0:
                out_string += "\n" + dec_to_hex(dec=l_dec)[2:] + " " \
                    + self.color_inrange(counter=l_dec, des_range=desired_range) + " "
            else:
                out_string += self.color_inrange(counter=l_dec, des_range=desired_range) + " "
            l_dec += 1

            progress_bar.update(1)

        logger.info("BULK READ SUCCESSFUL")
        return out_string


    def color_inrange(self, *, counter: int, des_range: range) -> str:
        """Colors the string in red.

        :param counter: An integer value (type int).
        :param des_range: An range object (type range).
        :return: Colored data value from RAM if the corresponding address in desired address space.
        """

        hex_addr = dec_to_hex(dec=counter)
        data = self.read_single_address(hex_address=hex_addr)
        return colored(data, "red") if counter in des_range else data


    @checksum_status_pbar
    def verify_checksum(
        self,
        addr_checksum_mappings: Dict[str, str],
        byte_count: Optional[str]="0x03",
        record_type: Optional[str]="0x00",
        progress_bar: Union[ContextManager, None]=None,
    ) -> str:
        """Verifies the checksum for addresses passed.

        :param addr_checksum_mappings: A dictionary containing address and corressponding checksum to be verified (type Dict[str:str]).
        :param byte_count: Byte count of data in hex (type string).
        :param record_type: Record type in hex (type string).
        :retrun: Returns a string having indivitual address checksum verification status (type string).
        """

        checksum_verified_status = []
        checksum_status_log = ""

        for addr, checksum in addr_checksum_mappings.items():
            data = self.read_single_address(hex_address=addr)
            read_record_without_checksum_string = "0x" + byte_count[2:] + addr[2:] \
                + record_type[2:] + data[2:]

            read_record_checksum = (
                # Converting to Hex instance
                Hex(hexString=read_record_without_checksum_string)
                # Checksum computation
                .checksum
            )

            checksum_verified: bool = checksum == read_record_checksum
            checksum_verified_status.append(checksum_verified)

            checksum_status_log += f"Checksum {('verification failed', 'verified')[checksum_verified]} for address: {addr}\n"

            progress_bar.update(1)

        if all(checksum_verified_status):
            # Blink the checksum verification led 4 times
            for x in range(1, 5):
               self.checksum_notifier.set_value(value=x % 2)
               time.sleep(.5)

        logger.info("CHECKSUM VERIFICATION DONE")
        return checksum_status_log


    def clear_addr_reg(self) -> None:
        """Clears the address shifter.

        :return: None.
        """

        self.addr_shifter.clear_register()


    def clear_data_reg(self) -> None:
        """Clears the data shifter.

        :return: None.
        """

        self.data_shifter.clear_register()

    def __repr__(self) -> str:
        """Returns representation of instance of RAM_Interface data class.

        :return: Representation of RAM_Interface class instance (type string).
        """

        return (f'{self.__class__.__name__}(R_Pins={self.R_Pins}, W_Pins={self.W_Pins}, addr_shifter={self.addr_shifter}, data_shifter={self.data_shifter})')
