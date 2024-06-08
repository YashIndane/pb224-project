#!/usr/bin/python3

from dataclasses import dataclass, field
from typing import Optional, List, Any
import RPi.GPIO as GPIO
import time


@dataclass(kw_only=True)
class Hex:
    hexString: str

    def hex_to_bin(self) -> str:
        scale = 16
        bit_length = 4 * (len(self.hexString) - 2)
        bin_data = bin(int(self.hexString, scale))[2:].zfill(bit_length)
        return bin_data

    def hex_to_dec(self) -> int:
        scale = 16
        dec_num = int(self.hexString, scale)
        return dec_num

    def bit_size(self) -> int:
        return 4 * (len(self.hexString) - 2)


@dataclass(kw_only=True)
class DigitalPin:
    pinNo: int
    mode: Any
    initialValue: Optional[int]=field(
        default=0
    )

    def trigger(self, transition: Optional[str]="1", time_period: Optional[int]=0.05) -> None:
        GPIO.output(self.pinNo, transition=="1")
        time.sleep(time_period)
        GPIO.output(self.pinNo, transition!="1")

    def set_value(self, value: int) -> None:
        GPIO.output(self.pinNo, value)

    # Sets the pin initial config
    def __post_init__(self) -> None:
        GPIO.setup(self.pinNo, self.mode, initial=self.initialValue)


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

