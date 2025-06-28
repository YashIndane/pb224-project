#!/usr/bin/python3

from dataclasses import dataclass, field
from typing import Optional, List
from digitalpin import DigitalPin
from pb224_utilities import Hex
import time


@dataclass(kw_only=True)
class Shifter:
    shifterDigitalPins: List[DigitalPin]
    shifterDelay: Optional[int]=field(
        default=0.1
    )

    def clear_register(self) -> None:
        """
        Clears the register.

        :return: None.
        """

        _SRCLR = self.shifterDigitalPins[-1]
        _SRCLR.trigger(transition="0")

    def shift(self, shiftHex: Hex) -> None:
        """
        Shifts the given data using 74HC595 shift registers.

        :param shiftHex: Hexadecimal representation of data to be shifted (type Hex).
        :return: None.
        """

        _SER, _SRCLK, _RCLK = self.shifterDigitalPins[0:3]
        _counter = 0
        _shift_num = shiftHex.hex_to_dec()

        while _counter < shiftHex.bit_size():
            _SER.set_value(value=_shift_num % 2)
            time.sleep(self.shifterDelay)
            _SRCLK.trigger(transition="1")
            _shift_num >>= 1
            _counter += 1

        time.sleep(self.shifterDelay)
        _RCLK.trigger(transition="1")
        _SER.set_value(value=0)

    def __repr__(self) -> str:
        """
        Returns representation of instance of Shifter data class.

        :return: Representation of Shifter data class instance (type string).
        """

        return (f'{self.__class__.__name__}(shifterDigitalPins={self.shifterDigitalPins}, shifterDelay={self.shifterDelay})')
