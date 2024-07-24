#!/usr/bin/python3

from shifter import Shifter
from digitalpin import DigitalPin
import ram_operations
import RPi.GPIO as GPIO
import time


if __name__ == "__main__":

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    # addrdata = "0x810d:0x6700bc"
    # addr, data = addrdata.split(":")

    DATA_SER   = DigitalPin(pinNo=23, mode=GPIO.OUT, initialValue=0)
    DATA_SRCLK = DigitalPin(pinNo=24, mode=GPIO.OUT, initialValue=0)
    DATA_RCLK  = DigitalPin(pinNo=15, mode=GPIO.OUT, initialValue=0)
    DATA_SRCLR = DigitalPin(pinNo=16, mode=GPIO.OUT, initialValue=1)

    data_shifter = Shifter(shifterDigitalPins=[DATA_SER, DATA_SRCLK, DATA_RCLK, DATA_SRCLR], shifterDelay=0.05)
    data_shifter.clear_register()

    ADDR_SER   = DigitalPin(pinNo=17, mode=GPIO.OUT, initialValue=0)
    ADDR_SRCLK = DigitalPin(pinNo=27, mode=GPIO.OUT, initialValue=0)
    ADDR_RCLK  = DigitalPin(pinNo=22, mode=GPIO.OUT, initialValue=0)
    ADDR_SRCLR = DigitalPin(pinNo=5, mode=GPIO.OUT, initialValue=1)

    address_shifter = Shifter(shifterDigitalPins=[ADDR_SER, ADDR_SRCLK, ADDR_RCLK, ADDR_SRCLR], shifterDelay=0.05)
    address_shifter.clear_register()

    # RAM write pins
    RI     = DigitalPin(pinNo=6, mode=GPIO.OUT, initialValue=0)
    RI_CLK = DigitalPin(pinNo=26, mode=GPIO.OUT, initialValue=0)

    # RAM Read pins
    LATCH       = DigitalPin(pinNo=13, mode=GPIO.OUT, initialValue=1)
    SHIFT_CLK   = DigitalPin(pinNo=4, mode=GPIO.OUT, initialValue=0)
    SER_DATA_IN = DigitalPin(pinNo=12, mode=GPIO.IN)

    ram_OP = ram_operations.RAM_Interface(
        R_Pins=[LATCH, SHIFT_CLK, SER_DATA_IN],
        W_Pins=[RI, RI_CLK],
        addr_shifter=address_shifter,
        data_shifter=data_shifter
    )

    #ram_OP.write_single_address(hex_address="0x0009", hex_data="0x000094")
    #time.sleep(0.05)
    #ram_OP.write_single_address(hex_address="0x0008", hex_data="0x000019")
    #time.sleep(0.05)
    #ram_OP.write_single_address(hex_address="0x0007", hex_data="0x0000ad")

    #time.sleep(0.05)
    #print(ram_OP.read_single_address(hex_address="0x0009"))
    #time.sleep(0.05)
    #print(ram_OP.read_single_address(hex_address="0x0008"))
    #time.sleep(0.05)
    #print(ram_OP.read_single_address(hex_address="0x0007"))

    # Clear registers
    # data_shifter.clear_register()
    # address_shifter.clear_register()

    GPIO.cleanup()
