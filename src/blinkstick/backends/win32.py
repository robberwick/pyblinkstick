"""
Windows-specific backend implementation for BlinkStick devices using pywinusb.

This module provides the Win32Backend class which implements communication with
BlinkStick devices on Windows systems using the pywinusb library. It handles:
- Device discovery and enumeration
- Serial number-based device lookup
- Low-level USB control transfers
- Feature report management
- Device reconnection logic

The backend maintains the connection state and handles device disconnection/reconnection
scenarios transparently to provide reliable device communication.
"""

from __future__ import annotations

import sys
from ctypes import *

from pywinusb import hid  # type: ignore

from blinkstick.constants import VENDOR_ID, PRODUCT_ID
from blinkstick.backends.base import BaseBackend
from blinkstick.devices import BlinkStickDevice
from blinkstick.exceptions import BlinkStickException
from blinkstick.models import SerialDetails


class Win32Backend(BaseBackend[hid.HidDevice]):
    """Backend implementation for interacting with BlinkStick devices using the Win32 API.

    This class provides methods to find, manage, and communicate with BlinkStick devices
    on a Windows platform using the HID (Human Interface Device) protocol. It encapsulates
    the device handling logic, including opening devices, finding reports, and sending or
    receiving control transfers. The class also provides utilities to identify devices by
    serial numbers and refresh device connections. It extends the BaseBackend to provide
    platform-specific functionality.

    :ivar reports: List of HID reports available for the BlinkStick device. This is populated
        when the device is opened and feature reports are retrieved.
    :type reports: list[hid.core.HidReport]
    """

    reports: list[hid.core.HidReport]

    def __init__(self, device: BlinkStickDevice[hid.HidDevice]):
        """
        Initializes the BlinkStick device wrapper and establishes a connection to the provided device.
        It manages the raw HID reports and retrieves the serial number of the device.

        :param device: An instance of `BlinkStickDevice` encapsulating an `hid.HidDevice`.
        :type device: BlinkStickDevice[hid.HidDevice]

        :raises RuntimeError: If the device cannot be opened or if there is an issue
            retrieving the feature reports.

        """
        super().__init__(device=device)
        if device:
            self.blinkstick_device.raw_device.open()
            self.reports = self.blinkstick_device.raw_device.find_feature_reports()
            self.serial = self.get_serial()

    @staticmethod
    def find_by_serial(serial: str) -> list[BlinkStickDevice[hid.HidDevice]] | None:
        """
        Find and return a list of BlinkStick devices matching the specified serial number.

        This method searches for attached BlinkStick devices using the Win32Backend, and
        then matches the serial details of each device against the specified serial number.
        If a match is found, it returns a list containing the corresponding device(s).
        If no devices match the given serial number, the method returns None.

        :param serial: The serial number of the BlinkStick device to search for.
        :type serial: str
        :return: A list of devices matching the specified serial number or None if no
            matching device is found.
        :rtype: list[BlinkStickDevice[hid.HidDevice]] | None
        """
        found_devices = Win32Backend.get_attached_blinkstick_devices()
        for d in found_devices:
            if d.serial_details.serial == serial:
                return [d]

        return None

    def _refresh_attached_blinkstick_device(self):
        """
        Refreshes the attached BlinkStick device by reinitializing the device
        connection and retrieving its feature reports. If the device is not
        currently attached, the method will return False.

        :raises RuntimeError: If the device cannot be reopened successfully.
        :return: True if the attached device is successfully refreshed and
            feature reports are retrieved, False if no device is currently
            attached.
        :rtype: bool
        """
        # TODO This is weird semantics. fix up return values to be more sensible
        if not self.blinkstick_device:
            return False
        if devices := self.find_by_serial(self.blinkstick_device.serial_details.serial):
            self.blinkstick_device = devices[0]
            self.blinkstick_device.raw_device.open()
            self.reports = self.blinkstick_device.raw_device.find_feature_reports()
            return True

    @staticmethod
    def get_attached_blinkstick_devices(
        find_all: bool = True,
    ) -> list[BlinkStickDevice[hid.HidDevice]]:
        """
        Gets a list of attached BlinkStick devices filtered by vendor and product ID. This method
        can return either all attached BlinkStick devices or only the first detected one based
        on the specified parameter.

        :param find_all: If True, retrieves all attached BlinkStick devices; if False, retrieves
                         only the first detected device, defaults to True
        :type find_all: bool, optional
        :return: A list of BlinkStickDevice objects representing the attached BlinkStick devices.
        :rtype: list[BlinkStickDevice[hid.HidDevice]]
        """
        devices = hid.HidDeviceFilter(
            vendor_id=VENDOR_ID, product_id=PRODUCT_ID
        ).get_devices()

        blinkstick_devices = [
            BlinkStickDevice(
                raw_device=device,
                serial_details=SerialDetails(serial=device.serial_number),
                manufacturer=device.vendor_name,
                version_attribute=device.version_number,
                description=device.product_name,
            )
            for device in devices
        ]
        if find_all:
            return blinkstick_devices

        return blinkstick_devices[:1]

    def control_transfer(
        self, bmRequestType, bRequest, wValue, wIndex, data_or_wLength
    ):
        """
        Handles a USB control transfer operation based on the provided parameters. This method
        supports different cases depending on the `bmRequestType` value. If the request type
        indicates sending a feature report, it attempts to send the data to the BlinkStick device.
        In case of failure, it attempts to refresh attached devices or raises an exception if
        communication with the BlinkStick device fails. For a different request type, it retrieves
        a report based on the provided `wValue` parameter.

        :param bmRequestType: USB control request type determining the transfer operation to perform
        :type bmRequestType: int
        :param bRequest: Request type identifier, though not explicitly utilized in this implementation
        :type bRequest: int
        :param wValue: Value specifying specific report or information required, interpreted differently
                       based on `bmRequestType`
        :type wValue: int
        :param wIndex: Index for optional functionality or selection, not explicitly utilized here
        :type wIndex: int
        :param data_or_wLength: Buffer containing data for transfer or specifying data length,
                                determined by context of the request
        :type data_or_wLength: Union[list[int], bytes, int]
        :raises BlinkStickException: Raised if the communication with the BlinkStick device fails
                                      after multiple attempts
        :return: Report data or None depending on the request type
        :rtype: Optional[int]
        """
        if bmRequestType == 0x20:
            if sys.version_info[0] < 3:
                data = (c_ubyte * len(data_or_wLength))(
                    *[c_ubyte(ord(c)) for c in data_or_wLength]
                )
            else:
                data = (c_ubyte * len(data_or_wLength))(
                    *[c_ubyte(c) for c in data_or_wLength]
                )
            data[0] = wValue
            if not self.blinkstick_device.raw_device.send_feature_report(data):
                if self._refresh_attached_blinkstick_device():
                    self.blinkstick_device.raw_device.send_feature_report(data)
                else:
                    raise BlinkStickException(
                        "Could not communicate with BlinkStick {0} - it may have been removed".format(
                            self.serial
                        )
                    )

        elif bmRequestType == 0x80 | 0x20:
            return self.reports[wValue - 1].get()
