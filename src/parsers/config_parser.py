#!/usr/bin/python3

"""Module to parse the pb224 assembler config file""""

from __future__ import annotations

import RPi.GPIO as GPIO
import yaml

from src.entities.shifter import Shifter
from src.entities.digitalpin import DigitalPin
from src.ram import ram_operations


def parse_config(*, conf_file: str) -> ram_operations.RAM_Interface:
    """Parses the pb224 config file and returns back the ram operations object.

    :param config_file: The path of pb224 config yaml file (type string).
    :return: ram operations object (type ram_operations.RAM_Interface).
    """

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    mode_selecter = (GPIO.OUT, GPIO.IN)

    with open(file=conf_file, mode="r") as config_file:
        configs = yaml.safe_load(config_file)
        config_file.close()


    # Parse data shifter profile
    data_shifter_profile_pins = (
        configs["config"]["profiles"][0]["sipoShifterProfiles"][0]["dataShifterProfile"]["pins"]
    )

    # DATA_SER
    data_ser_pin, data_ser_mode, data_ser_initval = data_shifter_profile_pins[0]["dataSER"].values()
    DATA_SER = DigitalPin(
        pinNo=data_ser_pin, mode=mode_selecter[data_ser_mode], initialValue=data_ser_initval
    )

    # DATA_SRCLK
    data_srclk_pin, data_srclk_mode, data_srclk_initval = data_shifter_profile_pins[1]["dataSRCLK"].values()
    DATA_SRCLK = DigitalPin(
        pinNo=data_srclk_pin, mode=mode_selecter[data_srclk_mode], initialValue=data_srclk_initval
    )

    # DATA_RCLK
    data_rclk_pin, data_rclk_mode, data_rclk_initval = data_shifter_profile_pins[2]["dataRCLK"].values()
    DATA_RCLK = DigitalPin(
        pinNo=data_rclk_pin, mode=mode_selecter[data_rclk_mode], initialValue=data_rclk_initval
    )

    # DATA_SRCLR
    data_srclr_pin, data_srclr_mode, data_srclr_initval = data_shifter_profile_pins[3]["dataSRCLR"].values()
    DATA_SRCLR = DigitalPin(
        pinNo=data_srclr_pin, mode=mode_selecter[data_srclr_mode], initialValue=data_srclr_initval
    )

    data_shifter = Shifter(
        shifterDigitalPins=[DATA_SER, DATA_SRCLK, DATA_RCLK, DATA_SRCLR],
        shifterDelay=.05
    )

    data_shifter.clear_register()


    # Parse address shifter profile
    addr_shifter_profile_pins = (
        configs["config"]["profiles"][0]["sipoShifterProfiles"][1]["addressShifterProfile"]["pins"]
    )

    # ADDR_SER
    addr_ser_pin, addr_ser_mode, addr_ser_initval = addr_shifter_profile_pins[0]["addressSER"].values()
    ADDR_SER = DigitalPin(
        pinNo=addr_ser_pin, mode=mode_selecter[addr_ser_mode], initialValue=addr_ser_initval
    )

    # ADDR_SRCLK
    addr_srclk_pin, addr_srclk_mode, addr_srclk_initval = addr_shifter_profile_pins[1]["addressSRCLK"].values()
    ADDR_SRCLK = DigitalPin(
        pinNo=addr_srclk_pin, mode=mode_selecter[addr_srclk_mode], initialValue=addr_srclk_initval
    )

    # ADDR_RCLK
    addr_rclk_pin, addr_rclk_mode, addr_rclk_initval = addr_shifter_profile_pins[2]["addressRCLK"].values()
    ADDR_RCLK = DigitalPin(
        pinNo=addr_rclk_pin, mode=mode_selecter[addr_rclk_mode], initialValue=addr_rclk_initval
    )

    # ADDR_SRCLR
    addr_srclr_pin, addr_srclr_mode, addr_srclr_initval = addr_shifter_profile_pins[3]["addressSRCLR"].values()
    ADDR_SRCLR = DigitalPin(
        pinNo=addr_srclr_pin, mode=mode_selecter[addr_srclr_mode], initialValue=addr_srclr_initval
    )

    address_shifter = Shifter(
        shifterDigitalPins=[ADDR_SER, ADDR_SRCLK, ADDR_RCLK, ADDR_SRCLR],
        shifterDelay=.05
    )

    address_shifter.clear_register()


    # Parse RAM serial read profile
    ram_serial_reader_profile_pins = (
        configs["config"]["profiles"][1]["pisoShifterProfiles"][0]["ramSerialReaderProfile"]["pins"]
    )

    # RR_LATCH
    rr_latch_pin, rr_latch_mode, rr_latch_initval = ram_serial_reader_profile_pins[0]["shifterLatch"].values()
    RR_LATCH = DigitalPin(
        pinNo=rr_latch_pin, mode=mode_selecter[rr_latch_mode], initialValue=rr_latch_initval
    )

    # RR_SHIFT_CLK
    rr_shiftclk_pin, rr_shiftclk_mode, rr_shiftclk_initval = ram_serial_reader_profile_pins[1]["shiftCLK"].values()
    RR_SHIFTCLK = DigitalPin(
        pinNo=rr_shiftclk_pin, mode=mode_selecter[rr_shiftclk_mode], initialValue=rr_shiftclk_initval
    )

    # RR_SER_DATA_IN
    rr_serialin_pin, rr_serialin_mode = ram_serial_reader_profile_pins[2]["serialDataIn"].values()
    RR_SER_DATAIN = DigitalPin(
        pinNo=rr_serialin_pin, mode=mode_selecter[rr_serialin_mode]
    )


    # Parse RAM write profle
    ram_write_profile_pins = configs["config"]["profiles"][2]["otherProfiles"][0]["ramWriteProfile"]["pins"]

    # RW_RI
    rw_ri_pin, rw_ri_mode, rw_ri_initval = ram_write_profile_pins[0]["ramIn"].values()
    RW_RI = DigitalPin(
        pinNo=rw_ri_pin, mode=mode_selecter[rw_ri_mode], initialValue=rw_ri_initval
    )

    # RW_RICLK
    rw_riclk_pin, rw_riclk_mode, rw_riclk_initval = ram_write_profile_pins[1]["ramInCLK"].values()
    RW_RICLK = DigitalPin(
        pinNo=rw_riclk_pin, mode=mode_selecter[rw_riclk_mode], initialValue=rw_riclk_initval
    )

    # Checksum Blinker
    checksum_blinker_profile = configs["config"]["profiles"][2]["otherProfiles"][1]["checkSumBlinker"]["pins"]

    # CHE_BLI
    ch_pin, ch_mode, ch_initval = checksum_blinker_profile[0]["notify"].values()
    CHE_BLI = DigitalPin(
        pinNo=ch_pin, mode=mode_selecter[ch_mode], initialValue=ch_initval
    )

    # Ram Operations Object
    ram_OP = ram_operations.RAM_Interface(
        R_Pins=[RR_LATCH, RR_SHIFTCLK, RR_SER_DATAIN],
        W_Pins=[RW_RI, RW_RICLK],
        addr_shifter=address_shifter,
        data_shifter=data_shifter,
        checksum_notifier=CHE_BLI
    )

    return ram_OP
