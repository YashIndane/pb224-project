#!/usr/bin/python3

from shifter import DigitalPin, Shifter, Hex
import threading
import RPi.GPIO as GPIO


# Writes data to RAM at given address
def write_single_record(ram_address: str, ram_data: str) -> None:

    # Shifting address and data
    address_shifter_thread = threading.Thread(
        target=address_shifter.shift,
        kwargs={
            'shiftHex': Hex(hexString=ram_address)
        }
    )

    data_shifter_thread = threading.Thread(
        target=data_shifter.shift,
        kwargs={
            'shiftHex': Hex(hexString=ram_data)
        }
    )

    address_shifter_thread.start()
    data_shifter_thread.start()
    address_shifter_thread.join()
    data_shifter_thread.join()

    print("Data written!!")


if __name__ == "__main__":

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    addrdata = "0x00bb:0x7700e9"
    addr, data = addrdata.split(":")

    DATA_SER   = DigitalPin(pinNo=23, mode=GPIO.OUT, initialValue=0)
    DATA_SRCLK = DigitalPin(pinNo=18, mode=GPIO.OUT, initialValue=0)
    DATA_RCLK  = DigitalPin(pinNo=15, mode=GPIO.OUT, initialValue=0)
    DATA_SRCLR = DigitalPin(pinNo=14, mode=GPIO.OUT, initialValue=1)

    data_shifter = Shifter(shifterDigitalPins=[DATA_SER, DATA_SRCLK, DATA_RCLK, DATA_SRCLR], shifterDelay=0.05)
    data_shifter.clear_register()

    ADDR_SER   = DigitalPin(pinNo=26, mode=GPIO.OUT, initialValue=0)
    ADDR_SRCLK = DigitalPin(pinNo=22, mode=GPIO.OUT, initialValue=0)
    ADDR_RCLK  = DigitalPin(pinNo=19, mode=GPIO.OUT, initialValue=0)
    ADDR_SRCLR = DigitalPin(pinNo=6, mode=GPIO.OUT, initialValue=1)

    address_shifter = Shifter(shifterDigitalPins=[ADDR_SER, ADDR_SRCLK, ADDR_RCLK, ADDR_SRCLR], shifterDelay=0.05)
    address_shifter.clear_register()

    write_single_record(ram_address=addr, ram_data=data)

    GPIO.cleanup()
