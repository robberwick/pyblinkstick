"""
The base module provides foundational abstractions for BlinkStick device backends.

This module defines the BaseBackend abstract base class, which serves as the interface
for different backend implementations that communicate with BlinkStick devices. The
backend system allows for different OS USB implementations while
maintaining a consistent interface for device control.

Key components:
- BaseBackend: Abstract base class defining the interface for device communication
- Generic type T: Represents the backend-specific device handle type

Example usage:
    class USBBackend(BaseBackend[USBDevice]):
        def control_transfer(self, bmRequestType, bRequest, wValue, wIndex, data_or_wLength):
            # Implementation for USB-specific control transfer
            ...

        @staticmethod
        def get_attached_blinkstick_devices(find_all=True):
            # Implementation to find USB BlinkStick devices
            ...
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from typing import TypeVar, Generic

from blinkstick import BlinkStickVariant
from blinkstick.devices import BlinkStickDevice

T = TypeVar("T")


class BaseBackend(ABC, Generic[T]):
    """
    BaseBackend serves as an abstract base class for managing BlinkStick devices.

    This class is designed to provide an interface for interacting with BlinkStick
    devices. It includes abstract methods that must be implemented by derived
    classes to handle device communication, discovery, and control. The class also
    provides several concrete methods for retrieving device-specific attributes,
    such as serial numbers, manufacturer details, version, descriptions, and
    variants.

    :ivar blinkstick_device: The BlinkStick device instance managed by this backend.
    :type blinkstick_device: BlinkStickDevice[T]
    """

    blinkstick_device: BlinkStickDevice[T]

    def __init__(self, device: BlinkStickDevice[T]):
        """
        Initialize the BaseBackend with a BlinkStick device.

        :param device: The BlinkStick device to be managed by this backend.
        :type device: BlinkStickDevice[T]
        """
        self.blinkstick_device = device

    @abstractmethod
    def _refresh_attached_blinkstick_device(self):
        """
        Refresh the state of the attached BlinkStick device.

        This abstract method must be implemented by derived classes to update
        the current state of the connected BlinkStick device.

        :raises NotImplementedError: When called directly on the base class.
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def get_attached_blinkstick_devices(
        find_all: bool = True,
    ) -> list[BlinkStickDevice[T]]:
        """
        Get a list of all attached BlinkStick devices.

        :param find_all: If True, find all attached devices; if False, find only the first device.
        :type find_all: bool
        :return: A list of found BlinkStick devices.
        :rtype: list[BlinkStickDevice[T]]
        :raises NotImplementedError: When called directly on the base class.
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def find_by_serial(serial: str) -> list[BlinkStickDevice[T]] | None:
        """
        Find BlinkStick devices by their serial number.

        :param serial: The serial number to search for.
        :type serial: str
        :return: List of matching devices or None if no devices are found.
        :rtype: list[BlinkStickDevice[T]] | None
        :raises NotImplementedError: When called directly on the base class.
        """
        raise NotImplementedError

    @abstractmethod
    def control_transfer(
        self,
        bmRequestType: int,
        bRequest: int,
        wValue: int,
        wIndex: int,
        data_or_wLength: bytes | int,
    ):
        """
        Perform a control transfer to the USB device.

        :param bmRequestType: The request type field for the setup packet.
        :type bmRequestType: int
        :param bRequest: The request field for the setup packet.
        :type bRequest: int
        :param wValue: The value field for the setup packet.
        :type wValue: int
        :param wIndex: The index field for the setup packet.
        :type wIndex: int
        :param data_or_wLength: Either the data to send or the number of bytes to receive.
        :type data_or_wLength: bytes | int
        :raises NotImplementedError: When called directly on the base class.
        """
        raise NotImplementedError

    def get_serial(self) -> str:
        """
        Get the serial number of the BlinkStick device.

        :return: The device's serial number.
        :rtype: str
        """
        return self.blinkstick_device.serial_details.serial

    def get_manufacturer(self) -> str:
        """
        Get the manufacturer name of the BlinkStick device.

        :return: The device's manufacturer name.
        :rtype: str
        """
        return self.blinkstick_device.manufacturer

    def get_version_attribute(self) -> int:
        """
        Get the version attribute of the BlinkStick device.

        :return: The device's version attribute.
        :rtype: int
        """
        return self.blinkstick_device.version_attribute

    def get_description(self) -> str:
        """
        Get the description of the BlinkStick device.

        :return: The device's description.
        :rtype: str
        """
        return self.blinkstick_device.description

    def get_variant(self) -> BlinkStickVariant:
        """
        Get the variant of the BlinkStick device.

        :return: The device's variant.
        :rtype: BlinkStickVariant
        """
        return self.blinkstick_device.variant
