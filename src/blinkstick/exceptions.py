"""
BlinkStick exception hierarchy.

This module defines all exceptions that can be raised by the BlinkStick library.
The hierarchy is organized as follows:
- BlinkStickException (base class)
  - NotConnected
  - USBBackendNotAvailable
  - RGBColorException
  - BlinkStickProException
    - BlinkStickProChannelException
    - BlinkStickProLEDException
"""

from __future__ import annotations


class BlinkStickException(Exception):
    """Base exception class for all BlinkStick-related errors."""

    pass


class NotConnected(BlinkStickException):
    """Exception raised when attempting to operate on a disconnected BlinkStick device."""

    pass


class USBBackendNotAvailable(BlinkStickException):
    """Exception raised when the USB backend required for device communication is not available."""

    pass


class RGBColorException(BlinkStickException):
    """Exception raised for invalid RGB color values or operations."""

    pass


class BlinkStickProException(BlinkStickException):
    """Base exception class for BlinkStick Pro specific errors."""

    pass


class BlinkStickProChannelException(BlinkStickProException):
    """
    Exception raised when an invalid channel number is specified.

    This exception is raised when attempting to access a channel that is
    out of the valid range for the BlinkStick Pro device.

    :ivar channel: The invalid channel number that caused the exception.
    :type channel: int
    """

    def __init__(self, channel: int) -> None:
        """
        Initialize the exception with the invalid channel number.

        :param channel: The channel number that was out of bounds.
        :type channel: int
        """
        super().__init__(f"Channel {channel} is not valid")


class BlinkStickProLEDException(BlinkStickProException):
    """
    Exception raised for invalid pixel operations on a specific channel in a
    BlinkStick Pro LED device.

    This exception is used to indicate that an operation involving a pixel and
    its associated channel is not valid, typically due to out-of-range indices
    or similar issues. It provides detailed contextual information about the
    problematic channel and pixel index.

    :ivar channel: The channel number in which the invalid operation occurred.
    :ivar index: The pixel index that caused the exception.
    """

    def __init__(self, channel: Channel, index: int) -> None:
        super().__init__(f"Invalid pixel {index} for channel {channel}")
