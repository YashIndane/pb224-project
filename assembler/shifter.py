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
        SRCLR = self.shifterDigitalPins[-1]
        SRCLR.trigger(transition="0")

    def shift(self, shiftHex: Hex) -> None:
        SER, SRCLK, RCLK = self.shifterDigitalPins[0:3]
        counter = 0
        shift_num = shiftHex.hex_to_dec()

        while counter < shiftHex.bit_size():
            SER.set_value(value=shift_num % 2)
            time.sleep(self.shifterDelay)
            SRCLK.trigger(transition="1")
            shift_num >>= 1
            counter += 1

        time.sleep(self.shifterDelay)
        RCLK.trigger(transition="1")
        SER.set_value(0)
