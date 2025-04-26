"""
Backend implementation for BlinkStick devices on Unix-like operating systems.

This module provides USB communication functionality for BlinkStick devices on Unix-like
systems (Linux, macOS, etc.) using the libusb backend through usb.core. It handles:

- Device detection and enumeration
- USB control transfers
- Kernel driver management
- Device reconnection logic
- Serial number based device identification

Requirements:
    - libusb: System library for USB device communication
    - python-usb: Python bindings for libusb

Usage:
    backend = UnixLikeBackend(blinkstick_device)
    devices = UnixLikeBackend.get_attached_blinkstick_devices()
    device = UnixLikeBackend.find_by_serial("BS000000-0000")

Note:
    This backend may require appropriate udev rules on Linux systems to allow
    non-root access to USB devices.
"""

from __future__ import annotations

import usb.core  # type: ignore
import usb.util  # type: ignore

from blinkstick.constants import VENDOR_ID, PRODUCT_ID
from blinkstick.backends.base import BaseBackend
from blinkstick.devices import BlinkStickDevice
from blinkstick.exceptions import BlinkStickException, USBBackendNotAvailable
from blinkstick.models import SerialDetails


class UnixLikeBackend(BaseBackend[usb.core.Device]):
    """
    Represents a backend for managing BlinkStick devices in a Unix-like environment.

    This class provides functionality to interact with BlinkStick devices, handle
    USB communications, manage device connections, and perform control transfers.
    It ensures proper management of kernel drivers and devices' serial numbers.
    This backend is specifically designed for Unix-like systems and works with
    libusb-based USB support.

    :ivar blinkstick_device: The BlinkStick device currently managed by the backend.
    :type blinkstick_device: BlinkStickDevice
    """

    def __init__(self, device: BlinkStickDevice[usb.core.Device]):
        """
        Initializes a new instance of the class, associating it with a BlinkStick device.

        The constructor takes a device instance of type BlinkStickDevice and initializes
        the class with it. If a valid device is provided, it attempts to open and configure
        the device for further operations.

        :param device: An instance of BlinkStickDevice representing the target USB device.
        :type device: BlinkStickDevice[usb.core.Device], optional

        :raises Exception: If there's an issue opening or configuring the associated device.
        """
        super().__init__(device=device)
        if device:
            self.open_device()

    def open_device(self) -> None:
        """
        Opens the BlinkStick device for communication.

        This method checks if the device is available and notifies if it cannot
        be found. If the device is active and has a kernel driver attached, it
        attempts to detach the kernel driver to allow control over the device.
        Any issues during detachment result in an exception.

        :raises BlinkStickException: If the device cannot be found or the kernel
            driver cannot be detached.
        """
        if self.blinkstick_device is None:
            raise BlinkStickException("Could not find BlinkStick...")

        if self.blinkstick_device.raw_device.is_kernel_driver_active(0):
            try:
                self.blinkstick_device.raw_device.detach_kernel_driver(0)
            except usb.core.USBError as e:
                raise BlinkStickException("Could not detach kernel driver: %s" % str(e))

    def _refresh_attached_blinkstick_device(self):
        """
        Refreshes the currently attached BlinkStick device by checking its serial details
        and attempting to reconnect it if found. If the device is not attached or not found,
        no action will be taken.

        :raises AttributeError: If `serial_details` or `serial` attribute access fails
            due to uninitialized or invalid `blinkstick_device`.

        :return: True if the device is found and successfully refreshed, False otherwise.
        :rtype: bool
        """
        if not self.blinkstick_device:
            return False
        if devices := self.find_by_serial(self.blinkstick_device.serial_details.serial):
            self.blinkstick_device = devices[0]
            self.open_device()
            return True

    @staticmethod
    def get_attached_blinkstick_devices(
        find_all: bool = True,
    ) -> list[BlinkStickDevice[usb.core.Device]]:
        """
        Retrieves all BlinkStick devices attached to the USB ports. By default, it attempts
        to find all devices unless otherwise specified. This method handles exceptions
        such as missing USB backends or permission issues and raises appropriate errors.

        :param find_all: Flag to determine whether to find all connected devices or just one,
            defaults to True
        :type find_all: bool, optional
        :raises USBBackendNotAvailable: When the USB backend cannot be found or accessed.
            This could be due to missing dependencies (e.g., libusb) or permission issues.
        :return: A list of BlinkStickDevice objects representing connected devices
        :rtype: list[BlinkStickDevice[usb.core.Device]]
        """
        try:
            raw_devices = (
                usb.core.find(
                    find_all=find_all, idVendor=VENDOR_ID, idProduct=PRODUCT_ID
                )
                or []
            )
        except usb.core.NoBackendError:
            # TODO: improve this error message to provide more information on how to remediate the problem
            raise USBBackendNotAvailable(
                "Could not find USB backend. Is libusb installed?"
            )

        try:
            devices = [
                # TODO: refactor this to DRY up the usb.util.get_string calls
                BlinkStickDevice(
                    raw_device=device,
                    serial_details=SerialDetails(
                        serial=str(usb.util.get_string(device, 3, 1033))
                    ),
                    manufacturer=str(usb.util.get_string(device, 1, 1033)),
                    version_attribute=device.bcdDevice,
                    description=str(usb.util.get_string(device, 2, 1033)),
                )
                for device in raw_devices
            ]
        except usb.core.USBError as e:
            # if the error is due to a permission issue, raise a more specific exception
            if "Operation not permitted" in str(e):
                raise USBBackendNotAvailable(
                    "Permission denied accessing USB backend. Does a udev rule need to be added?"
                )
            raise
        return devices

    @staticmethod
    def find_by_serial(serial: str) -> list[BlinkStickDevice[usb.core.Device]] | None:
        """
        Find a BlinkStick device by its serial number.

        Searches through the list of attached BlinkStick devices and
        returns the matching device based on the provided serial number.
        If no matching device is found, returns None.

        :param serial: The serial number of the BlinkStick device to be found.
        :type serial: str
        :return: A list containing the BlinkStickDevice object that matches
            the provided serial number, or None if no match is found.
        :rtype: list[BlinkStickDevice[usb.core.Device]] | None
        """
        found_devices = UnixLikeBackend.get_attached_blinkstick_devices()
        for d in found_devices:
            if d.serial_details.serial == serial:
                return [d]

        return None

    def control_transfer(
        self,
        bmRequestType: int,
        bRequest: int,
        wValue: int,
        wIndex: int,
        data_or_wLength: bytes | int,
    ):
        """
        Perform a USB control transfer with the BlinkStick device. This function attempts to
        communicate with the BlinkStick device backend using a USB control transfer. If the initial
        transfer fails due to a USB error, the function attempts to refresh the device connection
        and retry the transfer. If the device cannot be refreshed or reconnected, an exception
        specific to BlinkStick is raised.

        :param bmRequestType: The bit field providing information on the desired operation direction
            (host-to-device or device-to-host), request type (standard, class, vendor), and
            recipient (device, interface, endpoint, other).
        :type bmRequestType: int
        :param bRequest: The specific request to execute (e.g., a standard request like GET_STATUS or
            a vendor-specific request).
        :type bRequest: int
        :param wValue: A 16-bit parameter related to the specific request (e.g., descriptor index
            for GET_DESCRIPTOR).
        :type wValue: int
        :param wIndex: A 16-bit parameter representing the recipient information (e.g., interface
            index, endpoint index).
        :type wIndex: int
        :param data_or_wLength: Either a data buffer (bytes) for host-to-device transfers or the
            desired length of data (integer) for device-to-host transfers.
        :type data_or_wLength: bytes | int
        :raises usb.USBError: Raised when the initial control transfer fails due to a USB communication
            error.
        :raises BlinkStickException: Raised if the device cannot be refreshed or reconnected
            after a failed control transfer attempt. Indicates that the BlinkStick device might
            have been removed or is otherwise inaccessible.
        :return: The result of the USB control transfer as returned by the BlinkStick backend.
            Depends on the request type and data direction.
        :rtype: Any
        """
        try:
            return self.blinkstick_device.raw_device.ctrl_transfer(
                bmRequestType, bRequest, wValue, wIndex, data_or_wLength
            )
        except usb.USBError:
            # Could not communicate with BlinkStick backend
            # attempt to find it again based on serial

            if self._refresh_attached_blinkstick_device():
                return self.blinkstick_device.raw_device.ctrl_transfer(
                    bmRequestType, bRequest, wValue, wIndex, data_or_wLength
                )
            else:
                raise BlinkStickException(
                    "Could not communicate with BlinkStick {0} - it may have been removed".format(
                        self.blinkstick_device.serial_details.serial
                    )
                )
