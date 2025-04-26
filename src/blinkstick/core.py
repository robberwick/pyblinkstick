"""
Core module for BlinkStick device interaction and discovery.

This module provides the main interface for discovering and interacting with BlinkStick devices.
It handles platform-specific USB backend selection and provides functions to find and initialize
BlinkStick devices.

Functions:
    find_all(): Find all attached BlinkStick devices.
    find_first(): Find first attached BlinkStick.
    find_by_serial(serial): Find BlinkStick device by serial number.
    get_blinkstick_package_version(): Get the installed package version.
"""

from __future__ import annotations

import sys
from importlib.metadata import version
from typing import TYPE_CHECKING


if sys.platform == "win32":
    from blinkstick.backends.win32 import Win32Backend as USBBackend
else:
    from blinkstick.backends.unix_like import UnixLikeBackend as USBBackend

if TYPE_CHECKING:
    from blinkstick.clients import BlinkStick


def find_all() -> list[BlinkStick]:
    """
    Find and return all attached BlinkStick devices.

    This function searches for all attached BlinkStick devices using the USB backend
    and creates corresponding client instances for each detected device. If no
    devices are found, it returns an empty list.

    :return: A list of BlinkStickClient instances representing the connected
             BlinkStick devices. If no devices are found, the list will be empty.
    :rtype: list[BlinkStickClient]
    """
    from blinkstick.clients import BlinkStick

    result: list[BlinkStick] = []
    if (found_devices := USBBackend.get_attached_blinkstick_devices()) is None:
        return result
    for d in found_devices:
        result.extend([BlinkStick(device=d)])

    return result


def find_first() -> BlinkStick | None:
    """
    Find and return the first BlinkStick device connected to the system.

    This function utilizes the USBBackend to detect connected BlinkStick devices
    and returns the client for the first detected device. If no devices are
    found, it returns None.

    :raises USBError: If there is an issue accessing USB devices.

    :return: The client for the first BlinkStick device detected or None if no
        devices are found.
    :rtype: BlinkStickClient | None
    """
    from blinkstick.clients import BlinkStick

    blinkstick_devices = USBBackend.get_attached_blinkstick_devices(find_all=False)

    if blinkstick_devices:
        return BlinkStick(device=blinkstick_devices[0])

    return None


def find_by_serial(serial: str = "") -> BlinkStick | None:
    """
    Find a BlinkStick device by its serial number and return a client object.

    This function attempts to locate a BlinkStick device with the provided serial
    number using the USB backend. If a matching device is found, it creates and
    returns a client object for the device. If no devices are found, the function
    returns None.

    :param serial: The serial number of the BlinkStick device to locate, defaults to an empty string.
    :type serial: str, optional
    :raises ValueError: If the serial parameter is invalid.
    :return: A client object corresponding to the found device, or None if no matching device is found.
    :rtype: BlinkStickClient | None
    """

    devices = USBBackend.find_by_serial(serial=serial)

    if devices:
        return BlinkStick(device=devices[0])

    return None


def get_blinkstick_package_version() -> str:
    """
    Fetches the installed version of the `blinkstick` package.

    This function retrieves the version of the `blinkstick` package installed
    in the current Python environment using the `importlib.metadata.version`
    function. It allows checking the precise version currently in use.

    :raises PackageNotFoundError: If the `blinkstick` package is not installed.

    :return: The version of the `blinkstick` package as a string.
    :rtype: str
    """
    return version("blinkstick")
