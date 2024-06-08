#!/usr/bin/python3

from shifter import DigitalPin, Shifter, Hex
import RPi.GPIO as GPIO


if __name__ == "__main__":

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    addrdata = "0x023c:0x100001"
    addr, data = addrdata.split(":")

    DATA_SER   = DigitalPin(pinNo=23, mode=GPIO.OUT, initialValue=0)
    DATA_SRCLK = DigitalPin(pinNo=18, mode=GPIO.OUT, initialValue=0)
    DATA_RCLK  = DigitalPin(pinNo=15, mode=GPIO.OUT, initialValue=0)
    DATA_SRCLR = DigitalPin(pinNo=14, mode=GPIO.OUT, initialValue=1)


    address_shifter = Shifter(shifterDigitalPins=[DATA_SER, DATA_SRCLK, DATA_RCLK, DATA_SRCLR], shifterDelay=0.05)
    address_shifter.clear_register()

    address_shifter.shift(
        shiftHex = Hex(hexString=data)
    )

    GPIO.cleanup()

