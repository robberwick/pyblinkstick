"""
Enumeration classes for BlinkStick device variants, modes, and color channels.

This module provides the following enumerations:
- BlinkStickVariant: Different models and variants of BlinkStick devices
- Mode: Operating modes for BlinkStick devices (RGB, RGB_INVERSE, ADDRESSABLE)
- Channel: Color channels (RED, GREEN, BLUE) for LED control

These enumerations are used throughout the BlinkStick library to provide
type-safe options for device identification, operation modes, and color
manipulation.
"""

from __future__ import annotations

from enum import Enum, IntEnum


class BlinkStickVariant(Enum):
    """
    Enumeration representing different variants of BlinkStick devices.

    This class provides a mechanism to identify various BlinkStick device variants
    based on major version and version attributes. It offers human-readable descriptions
    associated with each variant and utility methods to map from version information
    to the appropriate variant.

    :ivar UNKNOWN: Represents an unknown BlinkStick variant.
    :type UNKNOWN: BlinkStickVariant
    :ivar BLINKSTICK: Represents the BlinkStick variant.
    :type BLINKSTICK: BlinkStickVariant
    :ivar BLINKSTICK_PRO: Represents the BlinkStick Pro variant.
    :type BLINKSTICK_PRO: BlinkStickVariant
    :ivar BLINKSTICK_STRIP: Represents the BlinkStick Strip variant.
    :type BLINKSTICK_STRIP: BlinkStickVariant
    :ivar BLINKSTICK_SQUARE: Represents the BlinkStick Square variant.
    :type BLINKSTICK_SQUARE: BlinkStickVariant
    :ivar BLINKSTICK_NANO: Represents the BlinkStick Nano variant.
    :type BLINKSTICK_NANO: BlinkStickVariant
    :ivar BLINKSTICK_FLEX: Represents the BlinkStick Flex variant.
    :type BLINKSTICK_FLEX: BlinkStickVariant
    """

    UNKNOWN = (0, "Unknown")
    BLINKSTICK = (1, "BlinkStick")
    BLINKSTICK_PRO = (2, "BlinkStick Pro")
    BLINKSTICK_STRIP = (3, "BlinkStick Strip")
    BLINKSTICK_SQUARE = (4, "BlinkStick Square")
    BLINKSTICK_NANO = (5, "BlinkStick Nano")
    BLINKSTICK_FLEX = (6, "BlinkStick Flex")

    @property
    def value(self) -> int:
        """
        The `value` property integer value of the enum.

        :return: Integer value of the enum.
        :rtype: int
        """
        return self._value_[0]

    @property
    def description(self) -> str:
        """
        Provides a string description of the enum value.

        :return: The description of the enum value, such as "BlinkStick" or "BlinkStick Pro.
        :rtype: str
        """
        return self._value_[1]

    @staticmethod
    def from_version_attrs(
        major_version: int, version_attribute: int | None
    ) -> "BlinkStickVariant":
        """
        Determine the appropriate BlinkStickVariant based on the given major version
        and version attribute. The method identifies and returns the type of BlinkStick
        device by evaluating the major version number and an optional version attribute
        value. If the combination does not match any known BlinkStick device, it
        returns BlinkStickVariant.UNKNOWN.

        :param major_version: The major version number of the BlinkStick device.
        :type major_version: int
        :param version_attribute: The version attribute of the BlinkStick device,
            defaults to None.
        :type version_attribute: int | None, optional
        :return: The corresponding BlinkStickVariant enum for the given version
            details.
        :rtype: BlinkStickVariant
        """
        if major_version == 1:
            return BlinkStickVariant.BLINKSTICK
        elif major_version == 2:
            return BlinkStickVariant.BLINKSTICK_PRO
        elif major_version == 3:
            if version_attribute == 0x200:
                return BlinkStickVariant.BLINKSTICK_SQUARE
            elif version_attribute == 0x201:
                return BlinkStickVariant.BLINKSTICK_STRIP
            elif version_attribute == 0x202:
                return BlinkStickVariant.BLINKSTICK_NANO
            elif version_attribute == 0x203:
                return BlinkStickVariant.BLINKSTICK_FLEX
        return BlinkStickVariant.UNKNOWN


class Mode(IntEnum):
    """Enumeration for different modes of operation.

    Defines modes such as RGB, RGB_INVERSE, and ADDRESSABLE which represent
    the different pixel types supported by BlinkStick devices.

    :ivar RGB: Represents standard RGB mode.
    :type RGB: int
    :ivar RGB_INVERSE: Represents inverse RGB mode.
    :type RGB_INVERSE: int
    :ivar ADDRESSABLE: Represents an addressable mode, used for LED strips and other devices with multiple LEDs.
    :type ADDRESSABLE: int
    """

    RGB = 1
    RGB_INVERSE = 2
    ADDRESSABLE = 3


class Channel(IntEnum):
    """
    Enum representing color channels.

    :ivar RED: Represents the red channel.
    :type RED: int
    :ivar GREEN: Represents the green channel.
    :type GREEN: int
    :ivar BLUE: Represents the blue channel.
    :type BLUE: int
    """

    RED = 0
    GREEN = 1
    BLUE = 2
