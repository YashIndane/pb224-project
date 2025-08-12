#!/usr/bin/python3

"""Module for all DigitalPin management

DigitalPins are the GPIO pins on the Raspberry Pi Zero 2W SBC.
This module holds all the functionality to manage this pins.
The pin mode is [GPIO.BCM]
"""

import time
import RPi.GPIO as GPIO

from pydantic import BaseModel, field_validator
from typing import Optional, Any


class DigitalPin(BaseModel):
    pinNo: int
    mode: bool
    initialValue: Optional[int]=0

    # Attribute validations
    @field_validator("pinNo")
    @classmethod
    def validate_pinNo_attr(cls, value: int) -> int:
        assert (
            instance(value, int) and value in range(0, 28)
        ), "`pinNo` attribute should be a integer value between `0` and `27`, both inclusive."
        return value


    @field_validator("mode")
    @classmethod
    def validate_mode_attr(cls, value: bool) -> bool:
        assert instance(value, bool), "`mode` attribute should be a `boolean`."
        return value


    @field_validator("initialValue")
    @classmethod
    def validate_initialValue_attr(cls, value: int) -> int:
        assert(
            instance(value, int) and value in range(0, 2)
        ), "`initialValue` attribute should be a integer value, either `0` or `1`."
        return value


    def trigger(self, *, transition: Optional[str]="1", time_period: Optional[int]=.05) -> None:
        """Pulses a pin according to transition.

        :param transition: 1 for high to low and 0 for vice versa (type string).
        :param time_period: Time period of the pulse in secs (type integer).
        :return: None.
        """

        GPIO.output(self.pinNo, transition=="1")
        time.sleep(time_period)
        GPIO.output(self.pinNo, transition!="1")


    def set_value(self, *, value: int) -> None:
        """Sets the pin to high or low.

        :param value: 0 for low, 1 for high (type integer).
        :return: None.
        """

        GPIO.output(self.pinNo, value)


    def read_value(self) -> bool:
        """Reads the value at pin.

        :return: True for 1, False for 0 (type bool).
        """

        return GPIO.input(self.pinNo)


    def __post_init__(self) -> None:
        """Sets the pin initial configuration.

        :return: None.
        """

        if self.mode == GPIO.OUT:
            GPIO.setup(self.pinNo, self.mode, initial=self.initialValue)
        else:
            GPIO.setup(self.pinNo, self.mode)


    def __repr__(self) -> str:
        """Returns representation of a instance of DigitalPin data class.

        :return: representation of DigitalPin instance (type string).
        """

        return (f'{self.__class__.__name__}(pinNo={self.pinNo}, mode={self.mode}, inittialValue={self.initialValue})')
