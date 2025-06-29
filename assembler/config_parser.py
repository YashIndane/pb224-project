#!/usr/bin/python3


from shifter import Shifter
from digitalpin import DigitalPin
import ram_operations
import RPi.GPIO as GPIO
import yaml


def parse_config(*, conf_file: str) -> ram_operations.RAM_Interface:
    """
    Parses the pb224 config file and returns back the ram operations object.

    :param config_file: The path of pb224 config yaml file (type string).
    :return: ram operations object (type ram_operations.RAM_Interface).
    """

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    with open(file=conf_file, mode="r") as _config_file:
        _configs = yaml.safe_load(_config_file)
        _config_file.close()


    # Parse data shifter profile
    _data_shifter_profile_pins = _configs["config"]["profiles"][0]["sipoShifterProfiles"][0]["dataShifterProfile"]["pins"]

    # DATA_SER
    _data_ser_pin, _data_ser_mode, _data_ser_initval = _data_shifter_profile_pins[0]["dataSER"].values()
    _DATA_SER = DigitalPin(pinNo=_data_ser_pin, mode=GPIO.IN if _data_ser_mode else GPIO.OUT, initialValue=_data_ser_initval)

    # DATA_SRCLK
    _data_srclk_pin, _data_srclk_mode, _data_srclk_initval = _data_shifter_profile_pins[1]["dataSRCLK"].values()
    _DATA_SRCLK = DigitalPin(pinNo=_data_srclk_pin, mode=GPIO.IN if _data_srclk_mode else GPIO.OUT, initialValue=_data_srclk_initval)

    # DATA_RCLK
    _data_rclk_pin, _data_rclk_mode, _data_rclk_initval = _data_shifter_profile_pins[2]["dataRCLK"].values()
    _DATA_RCLK = DigitalPin(pinNo=_data_rclk_pin, mode=GPIO.IN if _data_rclk_mode else GPIO.OUT, initialValue=_data_rclk_initval)

    # DATA_SRCLR
    _data_srclr_pin, _data_srclr_mode, _data_srclr_initval = _data_shifter_profile_pins[3]["dataSRCLR"].values()
    _DATA_SRCLR = DigitalPin(pinNo=_data_srclr_pin, mode=GPIO.IN if _data_srclr_mode else GPIO.OUT, initialValue=_data_srclr_initval)

    _data_shifter = Shifter(
        shifterDigitalPins=[_DATA_SER, _DATA_SRCLK, _DATA_RCLK, _DATA_SRCLR],
        shifterDelay=0.05
    )

    _data_shifter.clear_register()


    # Parse address shifter profile
    _addr_shifter_profile_pins = _configs["config"]["profiles"][0]["sipoShifterProfiles"][1]["addressShifterProfile"]["pins"]

    # ADDR_SER
    _addr_ser_pin, _addr_ser_mode, _addr_ser_initval = _addr_shifter_profile_pins[0]["addressSER"].values()
    _ADDR_SER = DigitalPin(pinNo=_addr_ser_pin, mode=GPIO.IN if _addr_ser_mode else GPIO.OUT, initialValue=_addr_ser_initval)

    # ADDR_SRCLK
    _addr_srclk_pin, _addr_srclk_mode, _addr_srclk_initval = _addr_shifter_profile_pins[1]["addressSRCLK"].values()
    _ADDR_SRCLK = DigitalPin(pinNo=_addr_srclk_pin, mode=GPIO.IN if _addr_srclk_mode else GPIO.OUT, initialValue=_addr_srclk_initval)

    # ADDR_RCLK
    _addr_rclk_pin, _addr_rclk_mode, _addr_rclk_initval = _addr_shifter_profile_pins[2]["addressRCLK"].values()
    _ADDR_RCLK = DigitalPin(pinNo=_addr_rclk_pin, mode=GPIO.IN if _addr_rclk_mode else GPIO.OUT, initialValue=_addr_rclk_initval)

    # ADDR_SRCLR
    _addr_srclr_pin, _addr_srclr_mode, _addr_srclr_initval = _addr_shifter_profile_pins[3]["addressSRCLR"].values()
    _ADDR_SRCLR = DigitalPin(pinNo=_addr_srclr_pin, mode=GPIO.IN if _addr_srclr_mode else GPIO.OUT, initialValue=_addr_srclr_initval)

    _address_shifter = Shifter(
        shifterDigitalPins=[_ADDR_SER, _ADDR_SRCLK, _ADDR_RCLK, _ADDR_SRCLR],
        shifterDelay=0.05
    )

    _address_shifter.clear_register()


    # Parse RAM serial read profile
    _ram_serial_reader_profile_pins = _configs["config"]["profiles"][1]["pisoShifterProfiles"][0]["ramSerialReaderProfile"]["pins"]

    # RR_LATCH
    _rr_latch_pin, _rr_latch_mode, _rr_latch_initval = _ram_serial_reader_profile_pins[0]["shifterLatch"].values()
    _RR_LATCH = DigitalPin(pinNo=_rr_latch_pin, mode=GPIO.IN if _rr_latch_mode else GPIO.OUT, initialValue=_rr_latch_initval)

    # RR_SHIFT_CLK
    _rr_shiftclk_pin, _rr_shiftclk_mode, _rr_shiftclk_initval = _ram_serial_reader_profile_pins[1]["shiftCLK"].values()
    _RR_SHIFTCLK = DigitalPin(pinNo=_rr_shiftclk_pin, mode=GPIO.IN if _rr_shiftclk_mode else GPIO.OUT, initialValue=_rr_shiftclk_initval)

    # RR_SER_DATA_IN
    _rr_serialin_pin, _rr_serialin_mode = _ram_serial_reader_profile_pins[2]["serialDataIn"].values()
    _RR_SER_DATAIN = DigitalPin(pinNo=_rr_serialin_pin, mode=GPIO.IN if _rr_serialin_mode else GPIO.OUT)


    # Parse RAM write profle
    _ram_write_profile_pins = _configs["config"]["profiles"][2]["otherProfiles"][0]["ramWriteProfile"]["pins"]

    # RW_RI
    _rw_ri_pin, _rw_ri_mode, _rw_ri_initval = _ram_write_profile_pins[0]["ramIn"].values()
    _RW_RI = DigitalPin(pinNo=_rw_ri_pin, mode=GPIO.IN if _rw_ri_mode else GPIO.OUT, initialValue=_rw_ri_initval)

    # RW_RICLK
    _rw_riclk_pin, _rw_riclk_mode, _rw_riclk_initval = _ram_write_profile_pins[1]["ramInCLK"].values()
    _RW_RICLK = DigitalPin(pinNo=_rw_riclk_pin, mode=GPIO.IN if _rw_riclk_mode else GPIO.OUT, initialValue=_rw_riclk_initval)

    # Checksum Blinker
    _checksum_blinker_profile = _configs["config"]["profiles"][2]["otherProfiles"][1]["checkSumBlinker"]["pins"]

    # CHE_BLI
    _ch_pin, _ch_mode, _ch_initval = _checksum_blinker_profile[0]["notify"].values()
    _CHE_BLI = DigitalPin(pinNo=_ch_pin, mode=GPIO.IN if _ch_mode else GPIO.OUT, initialValue=_ch_initval)


    # RAM Operations Object
    _ram_OP = ram_operations.RAM_Interface(
        R_Pins=[_RR_LATCH, _RR_SHIFTCLK, _RR_SER_DATAIN],
        W_Pins=[_RW_RI, _RW_RICLK],
        addr_shifter=_address_shifter,
        data_shifter=_data_shifter,
        checksum_notifier=_CHE_BLI

    )

    return _ram_OP
