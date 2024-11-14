#!/usr/bin/python3

import RPi.GPIO as GPIO
import config_parser
from pathlib import Path
import time


if __name__ == "__main__":

    path = Path(__file__).parent / "../pb224_config.yaml"
    ram_OP = config_parser.parse_config(conf_file=path)

    #ram_OP.write_single_address(hex_address="0x6400", hex_data="0x9a6211")
    #time.sleep(0.05)
    #ram_OP.write_single_address(hex_address="0x6411", hex_data="0xccc222")
    #time.sleep(0.05)
    #ram_OP.write_single_address(hex_address="0x7001", hex_data="0x56783b")
    #time.sleep(0.05)
    #ram_OP.write_single_address(hex_address="0x7002", hex_data="0xa8cc20")
    #time.sleep(0.05)
    #ram_OP.write_single_address(hex_address="0x6999", hex_data="0x030add")

    time.sleep(0.05)
    print(ram_OP.read_single_address(hex_address="0x6400"))
    time.sleep(0.05)
    print(ram_OP.read_single_address(hex_address="0x6411"))
    time.sleep(0.05)
    print(ram_OP.read_single_address(hex_address="0x7001"))
    time.sleep(0.05)
    print(ram_OP.read_single_address(hex_address="0x7002"))
    time.sleep(0.05)
    print(ram_OP.read_single_address(hex_address="0x6999"))

    ram_OP.clear_addr_reg()
    ram_OP.clear_data_reg()

    GPIO.cleanup()
