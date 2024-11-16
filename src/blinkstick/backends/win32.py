from __future__ import annotations

import sys
from ctypes import *

from pywinusb import hid

from blinkstick.constants import VENDOR_ID, PRODUCT_ID
from blinkstick.backends.base import BaseBackend
from blinkstick.exceptions import BlinkStickException


class Win32Backend(BaseBackend):
    def __init__(self, device=None):
        super().__init__()
        self.device = device
        if device:
            self.device.open()
            self.reports = self.device.find_feature_reports()
            self.serial =  self.get_serial()

    @staticmethod
    def find_by_serial(serial: str) -> list | None:
        devices = [d for d in Win32Backend.find_blinksticks()
                   if d.serial_number == serial]

        if len(devices) > 0:
            return devices


    def _refresh_device(self):
        # TODO This is weird semantics. fix up return values to be more sensible
        if not self.serial:
            return False
        if devices := self.find_by_serial(self.serial):
            self.device = devices[0]
            self.device.open()
            self.reports = self.device.find_feature_reports()
            return True

    @staticmethod
    def find_blinksticks(find_all: bool = True):
        devices = hid.HidDeviceFilter(vendor_id =VENDOR_ID, product_id =PRODUCT_ID).get_devices()
        if find_all:
            return devices
        elif len(devices) > 0:
            return devices[0]
        else:
            return None


    def control_transfer(self, bmRequestType, bRequest, wValue, wIndex, data_or_wLength):
        if bmRequestType == 0x20:
            if sys.version_info[0] < 3:
                data = (c_ubyte * len(data_or_wLength))(*[c_ubyte(ord(c)) for c in data_or_wLength])
            else:
                data = (c_ubyte * len(data_or_wLength))(*[c_ubyte(c) for c in data_or_wLength])
            data[0] = wValue
            if not self.device.send_feature_report(data):
                if self._refresh_device():
                    self.device.send_feature_report(data)
                else:
                    raise BlinkStickException("Could not communicate with BlinkStick {0} - it may have been removed".format(self.serial))

        elif bmRequestType == 0x80 | 0x20:
            return self.reports[wValue - 1].get()

    def get_serial(self) -> str:
        return str(self.device.serial_number)

    def get_manufacturer(self) -> str:
        return str(self.device.vendor_name)

    def get_version_attribute(self) -> int:
        return int(self.device.version_number)

    def get_description(self) -> str:
        return str(self.device.product_name)