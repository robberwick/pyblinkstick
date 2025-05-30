from __future__ import annotations

import sys

from blinkstick.animation.animator import Animator
from blinkstick.animation.blink import BlinkAnimation
from blinkstick.animation.morph import MorphAnimation
from blinkstick.animation.pulse import PulseAnimation
from blinkstick.colors import (
    RGBColor,
    NamedColor,
)
from blinkstick.devices import BlinkStickDevice
from blinkstick.enums import BlinkStickVariant, Mode, Channel
from blinkstick.exceptions import NotConnected
from blinkstick.utilities import string_to_info_block_data, convert_to_rgb_color

if sys.platform == "win32":
    from blinkstick.backends.win32 import Win32Backend as USBBackend
else:
    from blinkstick.backends.unix_like import UnixLikeBackend as USBBackend

"""
Main module to control BlinkStick and BlinkStick Pro devices.
"""


class BlinkStick:
    """
    BlinkStick class is designed to control regular BlinkStick devices, or BlinkStick Pro
    devices in Normal or Inverse modes. Please refer to L{BlinkStick.set_mode} for more details
    about BlinkStick Pro backend modes.

    Code examples on how you can use this class are available here:

    U{https://github.com/arvydas/blinkstick-python/wiki}
    """

    _inverse: bool
    _error_reporting = True
    _max_rgb_value: int

    backend: USBBackend

    def __init__(
        self, device: BlinkStickDevice | None = None, error_reporting: bool = True
    ):
        """
        Constructor for the class.

        @type  error_reporting: Boolean
        @param error_reporting: display errors if they occur during communication with the backend
        """
        self._error_reporting = error_reporting
        self._max_rgb_value = 255
        self._inverse = False
        self.animator = Animator(self)

        if device:
            self.backend = USBBackend(device)

    def __getattribute__(self, name):
        """Default all callables to require a backend unless they have the no_backend_required attribute"""
        attr = object.__getattribute__(self, name)
        if callable(attr) and not getattr(attr, "no_backend_required", False):

            def wrapper(*args, **kwargs):
                if not getattr(self, "backend", None):
                    raise NotConnected("No backend set")
                return attr(*args, **kwargs)

            return wrapper
        return attr

    def __repr__(self):
        try:
            serial = self.serial
            variant = self.variant.description
        except NotConnected:
            return "<BlinkStick: Not connected>"
        return f"<BlinkStick: Variant={variant} Serial={serial}>"

    def __str__(self):
        try:
            serial = self.serial
            variant = self.variant.description
        except NotConnected:
            return "Blinkstick - Not connected"
        return f"{variant} ({serial})"

    @property
    def serial(self) -> str:
        """
        Returns the serial number of backend.::

            BSnnnnnn-1.0
            ||  |    | |- Software minor version
            ||  |    |--- Software major version
            ||  |-------- Denotes sequential number
            ||----------- Denotes BlinkStick backend

        Software version defines the capabilities of the backend

        @rtype: str
        @return: Serial number of the backend
        """
        return self.backend.get_serial()

    @property
    def manufacturer(self) -> str:
        """
        Get the manufacturer of the backend

        @rtype: str
        @return: Device manufacturer's name
        """
        return self.backend.get_manufacturer()

    @property
    def variant(self) -> BlinkStickVariant:
        """
        Get the product variant of the backend.

        @rtype: int
        @return: BlinkStickVariant.UNKNOWN, BlinkStickVariant.BLINKSTICK, BlinkStickVariant.BLINKSTICK_PRO and etc
        """

        return self.backend.get_variant()

    @property
    def variant_string(self) -> str:
        """
        Get the product variant of the backend as string.

        @rtype: string
        @return: "BlinkStick", "BlinkStick Pro", etc
        """
        return self.variant.description

    @property
    def description(self) -> str:
        """
        Get the description of the backend

        @rtype: str
        @return: Device description
        """
        return self.backend.get_description()

    @property
    def error_reporting(self) -> bool:
        return self._error_reporting

    @error_reporting.setter
    def error_reporting(self, error_reporting: bool) -> None:
        """
        Enable or disable error reporting

        @type  error_reporting: Boolean
        @param error_reporting: display errors if they occur during communication with the backend
        """
        self._error_reporting = error_reporting

    def set_color(
        self, color: RGBColor | NamedColor | str, channel: Channel = Channel.RED, index: int = 0
    ) -> None:
        """
        Set the color to the backend. Color can be specified in the following formats:
            - RGBColor object
            - NamedColor object
            - CSS color name as defined here: U{http://www.w3.org/TR/css3-color/}
            - Hexadecimal color value in 3 or 6 digits, with or without a '#' prefix e.g. '#FF3366', 'FF3366', '#F3F', 'F3F'
        """
        target_color = convert_to_rgb_color(color)

        if self._inverse:
            # Inverse mode is enabled, so invert the color using the bitwise NOT operator (fancy!)
            target_color = ~target_color

        red, green, blue = target_color.remap_to_new_range(max_value=self.max_rgb_value)

        if index == 0 and channel == 0:
            control_string = bytes(bytearray([0, red, green, blue]))
            report_id = 0x0001
        else:
            control_string = bytes(bytearray([5, channel, index, red, green, blue]))
            report_id = 0x0005

        if self._error_reporting:
            self.backend.control_transfer(0x20, 0x9, report_id, 0, control_string)
        else:
            try:
                self.backend.control_transfer(0x20, 0x9, report_id, 0, control_string)
            except Exception:
                pass

    def _get_color(self, index: int = 0) -> RGBColor:
        if index == 0:
            device_bytes = self.backend.control_transfer(
                0x80 | 0x20, 0x1, 0x0001, 0, 33
            )
            if self._inverse:
                return RGBColor(
                    red=255 - device_bytes[1],
                    green=255 - device_bytes[2],
                    blue=255 - device_bytes[3],
                )
            else:
                return RGBColor(
                    red=device_bytes[1], green=device_bytes[2], blue=device_bytes[3]
                )
        else:
            data = self.get_led_data((index + 1) * 3)

            return RGBColor(
                red=data[index * 3 + 1], green=data[index * 3], blue=data[index * 3 + 2]
            )

    def _get_color_hex(self, index: int = 0) -> str:
        return self._get_color(index=index).hex

    def get_color(
        self,
        index: int = 0,
    ) -> RGBColor:
        """
        Get the color of the LED at the specified index.
        :param index:
        :return:
        """

        return self._get_color(index=index)

    def _determine_report_id(self, led_count: int) -> tuple[int, int]:
        report_id = 9
        max_leds = 64

        if led_count <= 8 * 3:
            max_leds = 8
            report_id = 6
        elif led_count <= 16 * 3:
            max_leds = 16
            report_id = 7
        elif led_count <= 32 * 3:
            max_leds = 32
            report_id = 8
        elif led_count <= 64 * 3:
            max_leds = 64
            report_id = 9

        return report_id, max_leds

    def set_led_data(self, channel: Channel, data: list[int]) -> None:
        """
        Send LED data frame.

        @type  channel: int
        @param channel: the channel which to send data to (R=0, G=1, B=2)
        @type  data: int[0..64*3]
        @param data: The LED data frame in GRB color_mode
        """

        report_id, max_leds = self._determine_report_id(len(data))

        report = [0, channel]

        for i in range(0, max_leds * 3):
            if len(data) > i:
                report.append(data[i])
            else:
                report.append(0)

        self.backend.control_transfer(0x20, 0x9, report_id, 0, bytes(bytearray(report)))

    def get_led_data(self, count: int) -> list[int]:
        """
        Get LED data frame on the backend.

        @type  count: int
        @param count: How much data to retrieve. Can be in the range of 0..64*3
        @rtype: int[0..64*3]
        @return: LED data currently stored in the RAM of the backend
        """

        report_id, max_leds = self._determine_report_id(count)

        device_bytes = self.backend.control_transfer(
            0x80 | 0x20, 0x1, report_id, 0, max_leds * 3 + 2
        )

        return device_bytes[2 : 2 + count * 3]

    @property
    def mode(self) -> int:
        """
        Get BlinkStick Pro mode. Device currently supports the following modes:

            - 0 - (default) use R, G and B channels to control single RGB LED
            - 1 - same as 0, but inverse mode
            - 2 - control up to 64 WS2812 individual LEDs per each R, G and B channel

        You can find out more about BlinkStick Pro modes:

        U{http://www.blinkstick.com/help/tutorials/blinkstick-pro-modes}

        @rtype: int
        @return: Device mode
        """

        device_bytes = self.backend.control_transfer(0x80 | 0x20, 0x1, 0x0004, 0, 2)

        if len(device_bytes) >= 2:
            return device_bytes[1]
        else:
            return -1

    @mode.setter
    def mode(self, mode: Mode | int) -> None:
        """
        Set backend mode for BlinkStick Pro. Device currently supports the following modes:

            - 0 - (default) use R, G and B channels to control single RGB LED
            - 1 - same as 0, but inverse mode
            - 2 - control up to 64 WS2812 individual LEDs per each R, G and B channel

        You can find out more about BlinkStick Pro modes:

        U{http://www.blinkstick.com/help/tutorials/blinkstick-pro-modes}

        @type  mode: int
        @param mode: Device mode to set
        """
        # If mode is an enum, get the value
        # this will allow the user to pass in the enum directly, and also gate the value to the enum values
        if not isinstance(mode, int):
            mode = Mode(mode).value
        control_string = bytes(bytearray([4, mode]))

        self.backend.control_transfer(0x20, 0x9, 0x0004, 0, control_string)

    @property
    def led_count(self) -> int:
        """
        Get number of LEDs for supported devices

        @rtype: int
        @return: Number of LEDs
        """

        device_bytes = self.backend.control_transfer(0x80 | 0x20, 0x1, 0x81, 0, 2)

        if len(device_bytes) >= 2:
            return device_bytes[1]
        else:
            return -1

    @led_count.setter
    def led_count(self, count: int) -> None:
        """
        Set number of LEDs for supported devices

        @type  count: int
        @param count: number of LEDs to control
        """
        control_string = bytes(bytearray([0x81, count]))

        self.backend.control_transfer(0x20, 0x9, 0x81, 0, control_string)

    @property
    def info_block1(self) -> str:
        """
        Get the infoblock1 of the backend.

        This is a 32 byte array that can contain any data. It's supposed to
        hold the "Name" of the backend making it easier to identify rather than
        a serial number.

        @rtype: str
        @return: InfoBlock1 currently stored on the backend
        """

        device_bytes = self.backend.control_transfer(0x80 | 0x20, 0x1, 0x0002, 0, 33)
        result = ""
        for i in device_bytes[1:]:
            if i == 0:
                break
            result += chr(i)
        return result

    @info_block1.setter
    def info_block1(self, data: str) -> None:
        """
        Sets the infoblock1 with specified string.

        It fills the rest of 32 bytes with zeros.

        @type  data: str
        @param data: InfoBlock1 for the backend to set
        """
        self.backend.control_transfer(
            0x20, 0x9, 0x0002, 0, string_to_info_block_data(data)
        )

    @property
    def info_block2(self) -> str:
        """
        Get the infoblock2 of the backend.

        This is a 32 byte array that can contain any data.

        @rtype: str
        @return: InfoBlock2 currently stored on the backend
        """
        device_bytes = self.backend.control_transfer(0x80 | 0x20, 0x1, 0x0003, 0, 33)
        result = ""
        for i in device_bytes[1:]:
            if i == 0:
                break
            result += chr(i)
        return result

    @info_block2.setter
    def info_block2(self, data: str) -> None:
        """
        Sets the infoblock2 with specified string.

        It fills the rest of 32 bytes with zeros.

        @type  data: str
        @param data: InfoBlock2 for the backend to set
        """
        self.backend.control_transfer(
            0x20, 0x9, 0x0003, 0, string_to_info_block_data(data)
        )

    def set_random_color(self) -> None:
        """
        Sets random color to the backend.
        """
        self.set_color("random")

    def turn_off(self) -> None:
        """
        Turns off LED.
        """
        self.set_color("black")

    def morph(
        self,
        color: RGBColor | NamedColor | str,
        channel: Channel = Channel.RED,
        index: int = 0,
        duration: int = 1000,
        steps: int = 50,
        immediate: bool = False,
    ) -> None:
        """
        Morph from the current color to the specified target color.
        If immediate=True, cancel any running animations and start this one immediately.
        """
        animation = MorphAnimation(self, color, channel, index, duration, steps)
        if immediate:
            self.animator.animate_immediately(animation)
        else:
            self.animator.queue_animation(animation)

    def blink(
        self,
        color: RGBColor | NamedColor | str,
        channel: Channel = Channel.RED,
        index: int = 0,
        repeats: int = 1,
        delay: int = 500,
        immediate: bool = False,
    ) -> None:
        """
        Blink the specified color.
        If immediate=True, cancel any running animations and start this one immediately.
        """
        animation = BlinkAnimation(self, color, channel, index, repeats, delay)
        if immediate:
            self.animator.animate_immediately(animation)
        else:
            self.animator.queue_animation(animation)

    def pulse(
        self,
        color: RGBColor | NamedColor | str,
        channel: Channel = Channel.RED,
        index: int = 0,
        repeats: int = 1,
        duration: int = 1000,
        steps: int = 50,
        immediate: bool = False,
    ) -> None:
        """
        Pulse the specified color.
        If immediate=True, cancel any running animations and start this one immediately.
        """
        target_color = convert_to_rgb_color(color)
        animation = PulseAnimation(
            self, target_color, channel, index, repeats, duration, steps
        )
        if immediate:
            self.animator.animate_immediately(animation)
        else:
            self.animator.queue_animation(animation)

    def stop_animations(self) -> None:
        """Stop all running and queued animations"""
        self.animator.stop()

    @property
    def inverse(self) -> bool:
        """
        Get the value of inverse mode. This applies only to BlinkStick. Please use L{set_mode} for BlinkStick Pro
        to permanently set the inverse mode to the backend.

        @rtype: bool
        @return: True if inverse mode, otherwise false
        """
        return self._inverse

    @inverse.setter
    def inverse(self, value: bool) -> None:
        """
        Set inverse mode. This applies only to BlinkStick. Please use L{set_mode} for BlinkStick Pro
        to permanently set the inverse mode to the backend.

        @type  value: bool
        @param value: True/False to set the inverse mode
        """
        if type(value) is str:
            value = value.lower() == "true"  # type: ignore
        self._inverse = bool(value)

    @property
    def max_rgb_value(self) -> int:
        """
        Get RGB color limit. {set_color} function will automatically remap
        the values to maximum set.

        @rtype: int
        @return: 0..255 maximum value for each R, G and B color
        """
        return self._max_rgb_value

    @max_rgb_value.setter
    def max_rgb_value(self, value: int) -> None:
        """
        Set RGB color limit. {set_color} function will automatically remap
        the values to maximum supplied.

        @type  value: int
        @param value: 0..255 maximum value for each R, G and B color
        """
        # convert to int and clamp to 0..255
        # TODO remap current color immediately
        value = max(0, min(255, int(value)))
        self._max_rgb_value = value
