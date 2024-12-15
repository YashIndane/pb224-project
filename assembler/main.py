#!/usr/bin/python3

import RPi.GPIO as GPIO
import config_parser
import ihexfile_parser
from pathlib import Path
import time


if __name__ == "__main__":
 
    # Parse pb224 config file
    config_file_path = Path(__file__).parent / "../pb224_config.yaml"
    ram_OP = config_parser.parse_config(conf_file=config_file_path)
    print(ram_OP)

    # Parse ihex file
    #ihex_file_path = Path(__file__).parent / "../ihexfile.hex"
    #hex_record_list = ihexfile_parser.parse_intel_hexfile(filename=ihex_file_path)

    # Dump intel hex file
    #address_checksum_mappings = ram_OP.dump_intel_hexfile(record_list=hex_record_list)
    #print(address_checksum_mappings)

    # Checksum Verification for above intel hex file after dump
    #ram_OP.verify_checksum(addr_checksum_mappings=address_checksum_mappings, byte_count="0x03", record_type="0x00")

    time.sleep(0.05)
    ram_OP.write_single_address(hex_address="0x1968", hex_data="0x37cca2")
    time.sleep(0.05)
    ram_OP.write_single_address(hex_address="0x1969", hex_data="0xc28155")
    time.sleep(0.05)
    ram_OP.write_single_address(hex_address="0x196a", hex_data="0xe80065")
    time.sleep(0.05)
    ram_OP.write_single_address(hex_address="0x196b", hex_data="0xa1b9d3")
    time.sleep(0.05)
    ram_OP.write_single_address(hex_address="0x196c", hex_data="0xf62011")

    #time.sleep(0.05)
    #print(ram_OP.read_single_address(hex_address="0x0015"))
    #time.sleep(0.05)
    #print(ram_OP.read_single_address(hex_address="0x0016"))
    #time.sleep(0.05)
    #print(ram_OP.read_single_address(hex_address="0x0017"))
    #time.sleep(0.05)
    #print(ram_OP.read_single_address(hex_address="0x0018"))
    #time.sleep(0.05)
    #print(ram_OP.read_single_address(hex_address="0x1618"))

    print(ram_OP.bulk_read(lower_addr="0x1968", upper_addr="0x196c"))

    ram_OP.clear_addr_reg()
    ram_OP.clear_data_reg()

    GPIO.cleanup()
