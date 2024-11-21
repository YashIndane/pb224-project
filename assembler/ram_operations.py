#!/usr/bin/python3

from dataclasses import dataclass
from typing import List
from pb224_utilities import Hex, bin_to_hex
from digitalpin import DigitalPin
from shifter import Shifter
import threading
import time


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
