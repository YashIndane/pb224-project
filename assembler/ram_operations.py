#!/usr/bin/python3

from dataclasses import dataclass
from typing import List
from pb224_utilities import Hex, bin_to_hex
from digitalpin import DigitalPin
from shifter import Shifter
import RPi.GPIO as GPIO
import threading
import time


@dataclass(kw_only=True)
class RAM_Interface:
    R_Pins: List[DigitalPin]  #(read_ld, clk, serial_out)
    W_Pins: List[DigitalPin]  #(RI, RI_clk)
    addr_shifter: Shifter
    data_shifter: Shifter


    def read_single_address(self, hex_address: str) -> str:
        """
        Example hex_address: '0x3e01'
        Example return data: '0x3400aa'
        """

        RI = self.W_Pins[0]
        LD, R_CLK, SER_DATA = self.R_Pins

        # RI disabled
        RI.set_value(0)

        # Set address
        self.addr_shifter.shift(shiftHex=Hex(hexString=hex_address))

        time.sleep(0.05)

        # Latch the RAM data in 74HC165
        LD.trigger(transition=0)

        time.sleep(0.05)

        # Shifting out and reading 3 bytes of data
        data_bin_string = ""

        for i in range(23):
            data_bin_string += "1" if GPIO.input(SER_DATA) else "0"
            R_CLK.trigger(transition=1)
            time.sleep(0.05)

        # Reverse the binary string
        data_bin_string = data_bin_string[::-1]

        return bin_to_hex(data_bin_string)


    def write_single_address(self, hex_address: str, hex_data: str) -> None:
        """
        Example hex_address: '0x3e01'
        Example hex_data: '0x3400aa'
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
        RI.set_value(1)
        time.sleep(0.05)
        RI_CLK.trigger(transition="1")
        time.sleep(0.05)
        RI.set_value(0)
        time.sleep(0.05)

        print("data written")
