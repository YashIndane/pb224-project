#!/usr/bin/python3

import RPi.GPIO as GPIO
import config_parser
from pathlib import Path
import time


if __name__ == "__main__":

    path = Path(__file__).parent / "../pb224_config.yaml"
    ram_OP = config_parser.parse_config(conf_file=path)

    print(ram_OP)

    ram_OP.write_single_address(hex_address="0x1968", hex_data="0x37cca2")
    time.sleep(0.05)
    ram_OP.write_single_address(hex_address="0x1974", hex_data="0xc28155")
    time.sleep(0.05)
    ram_OP.write_single_address(hex_address="0x1999", hex_data="0xe80065")
    time.sleep(0.05)
    ram_OP.write_single_address(hex_address="0x2006", hex_data="0xa1b9d3")
    time.sleep(0.05)
    ram_OP.write_single_address(hex_address="0x1618", hex_data="0xf62011")

    time.sleep(0.05)
    print(ram_OP.read_single_address(hex_address="0x1968"))
    time.sleep(0.05)
    print(ram_OP.read_single_address(hex_address="0x1974"))
    time.sleep(0.05)
    print(ram_OP.read_single_address(hex_address="0x1999"))
    time.sleep(0.05)
    print(ram_OP.read_single_address(hex_address="0x2006"))
    time.sleep(0.05)
    print(ram_OP.read_single_address(hex_address="0x1618"))

    ram_OP.clear_addr_reg()
    ram_OP.clear_data_reg()

    GPIO.cleanup()
