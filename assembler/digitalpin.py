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

    def trigger(self, transition: Optional[str]="1", time_period: Optional[int]=0.05) -> None:
        GPIO.output(self.pinNo, transition=="1")
        time.sleep(time_period)
        GPIO.output(self.pinNo, transition!="1")


    def set_value(self, value: int) -> None:
        GPIO.output(self.pinNo, value)


    def read_value(self) -> bool:
        return GPIO.input(self.pinNo)


    # Sets the pin initial config
    def __post_init__(self) -> None:
        if self.mode == GPIO.OUT:
            GPIO.setup(self.pinNo, self.mode, initial=self.initialValue)
        else:
            GPIO.setup(self.pinNo, self.mode)
