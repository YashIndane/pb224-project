#!/usr/bin/python3

from dataclasses import dataclass, field
from typing import Optional, Any
import time
import RPi.GPIO as GPIO


@dataclass(kw_only=True)
class DigitalPin:
    pinNo: int
    mode: Any
    initialValue: Optional[int]=field(
        default=0
    )


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
