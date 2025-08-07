#!/usr/bin/python3

from src.parser import ihexfile_parser
from src.parser import config_parser
from pathlib import Path

import RPi.GPIO as GPIO
import time
import os


if __name__ == "__main__":
    os.system("python3 --version")

    # Parse pb224 config file
    config_file_path = Path(__file__).parent / "../pb224_config.yaml"
    ram_OP = config_parser.parse_config(conf_file=config_file_path)
    print(ram_OP)

    # Parse ihex file
    ihex_file_path = Path(__file__).parent / "../ihexfile.hex"
    hex_record_list = ihexfile_parser.parse_intel_hexfile(filename=ihex_file_path)

    # Dump intel hex file
    address_checksum_mappings = ram_OP.dump_intel_hexfile(record_list=hex_record_list)
    print(address_checksum_mappings)

    # Checksum Verification for above intel hex file after dump
    checksum_status_log = ram_OP.verify_checksum(
        addr_checksum_mappings=address_checksum_mappings
    )
    print(checksum_status_log)

    #time.sleep(0.05)
    #ram_OP.write_single_address(hex_address="0x1003", hex_data="0x37cca2")
    #time.sleep(0.05)
    #ram_OP.write_single_address(hex_address="0x1004", hex_data="0xc28155")
    #time.sleep(0.05)
    #ram_OP.write_single_address(hex_address="0x1005", hex_data="0xe80065")
    #time.sleep(0.05)
    #ram_OP.write_single_address(hex_address="0x1006", hex_data="0xa1b9d3")
    #time.sleep(0.05)
    #ram_OP.write_single_address(hex_address="0x1007", hex_data="0xf62011")

    #time.sleep(0.05)
    #print(ram_OP.read_single_address(hex_address="0x0015"))
    #time.sleep(0.05)
    #print(ram_OP.read_single_address(hex_address="0x0016"))
    #time.sleep(0.05)
    #print(ram_OP.read_single_address(hex_address="0x1003"))
    #time.sleep(0.05)
    #print(ram_OP.read_single_address(hex_address="0x1004"))
    #time.sleep(0.05)
    print(ram_OP.read_single_address(hex_address="0x1004"))

    #bulk_read_log = ram_OP.bulk_read(lower_addr="0x1001", upper_addr="0x100b")
    #print(bulk_read_log)

    ram_OP.clear_addr_reg()
    ram_OP.clear_data_reg()

    GPIO.cleanup()
