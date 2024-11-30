from __future__ import annotations

import sys
import time
import warnings
from importlib.metadata import version
from typing import Callable

from blinkstick.colors import (
    hex_to_rgb,
    name_to_rgb,
    remap_color,
    remap_rgb_value,
    remap_rgb_value_reverse,
    ColorFormat,
)
from blinkstick.constants import VENDOR_ID, PRODUCT_ID, BlinkStickVariant
from blinkstick.devices.device import BlinkStickDevice
from blinkstick.exceptions import BlinkStickException
from blinkstick.utilities import string_to_info_block_data

if sys.platform == "win32":
    from blinkstick.backends.win32 import Win32Backend as USBBackend
    import pywinusb.hid as hid  # type: ignore
else:
    from blinkstick.backends.unix_like import UnixLikeBackend as USBBackend
    import usb.core  # type: ignore
    import usb.util  # type: ignore

from random import randint

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

    inverse: bool
    error_reporting = True
    max_rgb_value: int

    backend: USBBackend
    bs_serial: str

    def __init__(
        self, device: BlinkStickDevice | None = None, error_reporting: bool = True
    ):
        """
        Constructor for the class.

        @type  error_reporting: Boolean
        @param error_reporting: display errors if they occur during communication with the backend
        """
        self.error_reporting = error_reporting
        self.max_rgb_value = 255
        self.inverse = False

        if device:
            self.backend = USBBackend(device)
            self.bs_serial = self.get_serial()

    def get_serial(self) -> str:
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

    def get_manufacturer(self) -> str:
        """
        Get the manufacturer of the backend

        @rtype: str
        @return: Device manufacturer's name
        """
        return self.backend.get_manufacturer()

    def get_variant(self) -> BlinkStickVariant:
        """
        Get the product variant of the backend.

        @rtype: int
        @return: BlinkStickVariant.UNKNOWN, BlinkStickVariant.BLINKSTICK, BlinkStickVariant.BLINKSTICK_PRO and etc
        """

        serial = self.get_serial()
        major = serial[-3]

        version_attribute = self.backend.get_version_attribute()

        return BlinkStickVariant.identify(int(major), version_attribute)

    def get_variant_string(self) -> str:
        """
        Get the product variant of the backend as string.

        @rtype: string
        @return: "BlinkStick", "BlinkStick Pro", etc
        """
        return self.get_variant().description

    def get_description(self) -> str:
        """
        Get the description of the backend

        @rtype: str
        @return: Device description
        """
        return self.backend.get_description()

    def set_error_reporting(self, error_reporting: bool) -> None:
        """
        Enable or disable error reporting

        @type  error_reporting: Boolean
        @param error_reporting: display errors if they occur during communication with the backend
        """
        self.error_reporting = error_reporting

    def set_color(
        self,
        channel: int = 0,
        index: int = 0,
        red: int = 0,
        green: int = 0,
        blue: int = 0,
        name: str | None = None,
        hex: str | None = None,
    ) -> None:
        """
        Set the color to the backend as RGB

        @type  channel: int
        @param channel: the channel which to send data to (R=0, G=1, B=2)
        @type  index: int
        @param index: the index of the LED
        @type  red: int
        @param red: Red color intensity 0 is off, 255 is full red intensity
        @type  green: int
        @param green: Green color intensity 0 is off, 255 is full green intensity
        @type  blue: int
        @param blue: Blue color intensity 0 is off, 255 is full blue intensity
        @type  name: str
        @param name: Use CSS color name as defined here: U{http://www.w3.org/TR/css3-color/}
        @type  hex: str
        @param hex: Specify color using hexadecimal color value e.g. '#FF3366'
        """

        red, green, blue = self._determine_rgb(
            red=red, green=green, blue=blue, name=name, hex=hex
        )

        r = int(round(red, 3))
        g = int(round(green, 3))
        b = int(round(blue, 3))

        if self.inverse:
            r, g, b = 255 - r, 255 - g, 255 - b

        if index == 0 and channel == 0:
            control_string = bytes(bytearray([0, r, g, b]))
            report_id = 0x0001
        else:
            control_string = bytes(bytearray([5, channel, index, r, g, b]))
            report_id = 0x0005

        if self.error_reporting:
            self.backend.control_transfer(0x20, 0x9, report_id, 0, control_string)
        else:
            try:
                self.backend.control_transfer(0x20, 0x9, report_id, 0, control_string)
            except Exception:
                pass

    def _determine_rgb(
        self,
        red: int = 0,
        green: int = 0,
        blue: int = 0,
        name: str | None = None,
        hex: str | None = None,
    ) -> tuple[int, int, int]:

        try:
            if name:
                # Special case for name="random"
                if name == "random":
                    red = randint(0, 255)
                    green = randint(0, 255)
                    blue = randint(0, 255)
                else:
                    red, green, blue = name_to_rgb(name)
            elif hex:
                red, green, blue = hex_to_rgb(hex)
        except ValueError:
            red = green = blue = 0

        red, green, blue = remap_rgb_value((red, green, blue), self.max_rgb_value)

        # TODO - do smarts to determine input type from red var in case it is not int

        return red, green, blue

    def _get_color_rgb(self, index: int = 0) -> tuple[int, int, int]:
        if index == 0:
            device_bytes = self.backend.control_transfer(
                0x80 | 0x20, 0x1, 0x0001, 0, 33
            )
            if self.inverse:
                return (
                    255 - device_bytes[1],
                    255 - device_bytes[2],
                    255 - device_bytes[3],
                )
            else:
                return device_bytes[1], device_bytes[2], device_bytes[3]
        else:
            data = self.get_led_data((index + 1) * 3)

            return data[index * 3 + 1], data[index * 3], data[index * 3 + 2]

    def _get_color_hex(self, index: int = 0) -> str:
        r, g, b = self._get_color_rgb(index)
        return "#%02x%02x%02x" % (r, g, b)

    def get_color(
        self,
        index: int = 0,
        color_mode: ColorFormat = ColorFormat.RGB,
        color_format: str | None = None,
    ) -> tuple[int, int, int] | str:
        """
        Get the current backend color in the defined format.

        Currently supported formats:

            1. rgb (default) - Returns values as 3-tuple (r,g,b)
            2. hex - returns current backend color as hexadecimal string

            >>> b = blinkstick.find_first()
            >>> b.set_color(red=255,green=0,blue=0)
            >>> (r,g,b) = b.get_color() # Get color as rbg tuple
            (255,0,0)
            >>> hex = b.get_color(color_mode=ColorFormat.HEX) # Get color as hex string
            '#ff0000'

        @type  index: int
        @param index: the index of the LED
        @type  color_mode: ColorFormat
        @param color_mode: the format to return the color in (ColorFormat.RGB or ColorFormat.HEX) - defaults to ColorFormat.RGB
        @type  color_format: str
        @param color_format: "rgb" or "hex". Defaults to "rgb". Deprecated, use color_mode instead.

        @rtype: (int, int, int) or str
        @return: Either 3-tuple for R, G and B values, or hex string
        """
        # color_format is deprecated, and color_mode should be used instead
        # if color_format is specified, then raise a DeprecationWarning, but attempt to convert it to a ColorFormat enum
        # if it's not possible, then default to ColorFormat.RGB, in line with the previous behavior
        if color_format:
            warnings.warn(
                "color_format is deprecated, please use color_mode instead",
                DeprecationWarning,
            )
            try:
                color_mode = ColorFormat.from_name(color_format)
            except ValueError:
                color_mode = ColorFormat.RGB

        color_funcs: dict[ColorFormat, Callable[[int], tuple[int, int, int] | str]] = {
            ColorFormat.RGB: self._get_color_rgb,
            ColorFormat.HEX: self._get_color_hex,
        }

        return color_funcs.get(color_mode, self._get_color_rgb)(index)

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

    def set_led_data(self, channel: int, data: list[int]) -> None:
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

    def set_mode(self, mode: int) -> None:
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
        control_string = bytes(bytearray([4, mode]))

        self.backend.control_transfer(0x20, 0x9, 0x0004, 0, control_string)

    def get_mode(self) -> int:
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

    def set_led_count(self, count: int) -> None:
        """
        Set number of LEDs for supported devices

        @type  count: int
        @param count: number of LEDs to control
        """
        control_string = bytes(bytearray([0x81, count]))

        self.backend.control_transfer(0x20, 0x9, 0x81, 0, control_string)

    def get_led_count(self) -> int:
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

    def get_info_block1(self) -> str:
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

    def get_info_block2(self) -> str:
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

    def set_info_block1(self, data: str) -> None:
        """
        Sets the infoblock1 with specified string.

        It fills the rest of 32 bytes with zeros.

        @type  data: str
        @param data: InfoBlock1 for the backend to set
        """
        self.backend.control_transfer(
            0x20, 0x9, 0x0002, 0, string_to_info_block_data(data)
        )

    def set_info_block2(self, data: str) -> None:
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
        self.set_color(name="random")

    def turn_off(self) -> None:
        """
        Turns off LED.
        """
        self.set_color()

    def pulse(
        self,
        channel: int = 0,
        index: int = 0,
        red: int = 0,
        green: int = 0,
        blue: int = 0,
        name: str | None = None,
        hex: str | None = None,
        repeats: int = 1,
        duration: int = 1000,
        steps: int = 50,
    ) -> None:
        """
        Morph to the specified color from black and back again.

        @type  channel: int
        @param channel: the channel which to send data to (R=0, G=1, B=2)
        @type  index: int
        @param index: the index of the LED
        @type  red: int
        @param red: Red color intensity 0 is off, 255 is full red intensity
        @type  green: int
        @param green: Green color intensity 0 is off, 255 is full green intensity
        @type  blue: int
        @param blue: Blue color intensity 0 is off, 255 is full blue intensity
        @type  name: str
        @param name: Use CSS color name as defined here: U{http://www.w3.org/TR/css3-color/}
        @type  hex: str
        @param hex: Specify color using hexadecimal color value e.g. '#FF3366'
        @type  repeats: int
        @param repeats: Number of times to pulse the LED
        @type  duration: int
        @param duration: Duration for pulse in milliseconds
        @type  steps: int
        @param steps: Number of gradient steps
        """
        self.turn_off()
        for x in range(repeats):
            self.morph(
                channel=channel,
                index=index,
                red=red,
                green=green,
                blue=blue,
                name=name,
                hex=hex,
                duration=duration,
                steps=steps,
            )
            self.morph(
                channel=channel,
                index=index,
                red=0,
                green=0,
                blue=0,
                duration=duration,
                steps=steps,
            )

    def blink(
        self,
        channel: int = 0,
        index: int = 0,
        red: int = 0,
        green: int = 0,
        blue: int = 0,
        name: str | None = None,
        hex: str | None = None,
        repeats: int = 1,
        delay: int = 500,
    ) -> None:
        """
        Blink the specified color.

        @type  channel: int
        @param channel: the channel which to send data to (R=0, G=1, B=2)
        @type  index: int
        @param index: the index of the LED
        @type  red: int
        @param red: Red color intensity 0 is off, 255 is full red intensity
        @type  green: int
        @param green: Green color intensity 0 is off, 255 is full green intensity
        @type  blue: int
        @param blue: Blue color intensity 0 is off, 255 is full blue intensity
        @type  name: str
        @param name: Use CSS color name as defined here: U{http://www.w3.org/TR/css3-color/}
        @type  hex: str
        @param hex: Specify color using hexadecimal color value e.g. '#FF3366'
        @type  repeats: int
        @param repeats: Number of times to pulse the LED
        @type  delay: int
        @param delay: time in milliseconds to light LED for, and also between blinks
        """
        ms_delay = float(delay) / float(1000)
        for x in range(repeats):
            if x:
                time.sleep(ms_delay)
            self.set_color(
                channel=channel,
                index=index,
                red=red,
                green=green,
                blue=blue,
                name=name,
                hex=hex,
            )
            time.sleep(ms_delay)
            self.set_color(channel=channel, index=index)

    def morph(
        self,
        channel: int = 0,
        index: int = 0,
        red: int = 0,
        green: int = 0,
        blue: int = 0,
        name: str | None = None,
        hex: str | None = None,
        duration: int = 1000,
        steps: int = 50,
    ) -> None:
        """
        Morph to the specified color.

        @type  channel: int
        @param channel: the channel which to send data to (R=0, G=1, B=2)
        @type  index: int
        @param index: the index of the LED
        @type  red: int
        @param red: Red color intensity 0 is off, 255 is full red intensity
        @type  green: int
        @param green: Green color intensity 0 is off, 255 is full green intensity
        @type  blue: int
        @param blue: Blue color intensity 0 is off, 255 is full blue intensity
        @type  name: str
        @param name: Use CSS color name as defined here: U{http://www.w3.org/TR/css3-color/}
        @type  hex: str
        @param hex: Specify color using hexadecimal color value e.g. '#FF3366'
        @type  duration: int
        @param duration: Duration for morph in milliseconds
        @type  steps: int
        @param steps: Number of gradient steps (default 50)
        """

        r_end, g_end, b_end = self._determine_rgb(
            red=red, green=green, blue=blue, name=name, hex=hex
        )
        # descale the above values
        r_end, g_end, b_end = remap_rgb_value_reverse(
            (r_end, g_end, b_end), self.max_rgb_value
        )

        r_start, g_start, b_start = remap_rgb_value_reverse(
            self._get_color_rgb(index), self.max_rgb_value
        )

        if r_start > 255 or g_start > 255 or b_start > 255:
            r_start = 0
            g_start = 0
            b_start = 0

        gradient = []

        steps += 1
        for n in range(1, steps):
            d = 1.0 * n / steps
            r = (r_start * (1 - d)) + (r_end * d)
            g = (g_start * (1 - d)) + (g_end * d)
            b = (b_start * (1 - d)) + (b_end * d)

            gradient.append((r, g, b))

        ms_delay = float(duration) / float(1000 * steps)

        self.set_color(
            channel=channel, index=index, red=r_start, green=g_start, blue=b_start
        )

        for grad in gradient:
            grad_r, grad_g, grad_b = map(int, grad)

            self.set_color(
                channel=channel, index=index, red=grad_r, green=grad_g, blue=grad_b
            )
            time.sleep(ms_delay)

        self.set_color(channel=channel, index=index, red=r_end, green=g_end, blue=b_end)

    def open_device(self, d):
        """Open backend.
        @param d: Device to open
        """
        if self.backend is None:
            raise BlinkStickException("Could not find BlinkStick...")

        if self.backend.is_kernel_driver_active(0):
            try:
                self.backend.detach_kernel_driver(0)
            except usb.core.USBError as e:
                raise BlinkStickException("Could not detach kernel driver: %s" % str(e))

        return True

    def get_inverse(self) -> bool:
        """
        Get the value of inverse mode. This applies only to BlinkStick. Please use L{set_mode} for BlinkStick Pro
        to permanently set the inverse mode to the backend.

        @rtype: bool
        @return: True if inverse mode, otherwise false
        """
        return self.inverse

    def set_inverse(self, value: bool) -> None:
        """
        Set inverse mode. This applies only to BlinkStick. Please use L{set_mode} for BlinkStick Pro
        to permanently set the inverse mode to the backend.

        @type  value: bool
        @param value: True/False to set the inverse mode
        """
        if type(value) is str:
            value = value.lower() == "true"  # type: ignore
        self.inverse = bool(value)

    def set_max_rgb_value(self, value: int) -> None:
        """
        Set RGB color limit. {set_color} function will automatically remap
        the values to maximum supplied.

        @type  value: int
        @param value: 0..255 maximum value for each R, G and B color
        """
        # convert to int and clamp to 0..255
        value = max(0, min(255, int(value)))
        self.max_rgb_value = value

    def get_max_rgb_value(self) -> int:
        """
        Get RGB color limit. {set_color} function will automatically remap
        the values to maximum set.

        @rtype: int
        @return: 0..255 maximum value for each R, G and B color
        """
        return self.max_rgb_value


class BlinkStickPro:
    """
    BlinkStickPro class is specifically designed to control the individually
    addressable LEDs connected to the backend. The tutorials section contains
    all the details on how to connect them to BlinkStick Pro.

    U{http://www.blinkstick.com/help/tutorials}

    Code example on how you can use this class are available here:

    U{https://github.com/arvydas/blinkstick-python/wiki#code-examples-for-blinkstick-pro}
    """

    r_led_count: int
    g_led_count: int
    b_led_count: int
    fps_count: int
    data_transmission_delay: float
    max_rgb_value: int
    data: list[list[list[int]]]
    bstick: BlinkStick | None

    def __init__(
        self,
        r_led_count: int = 0,
        g_led_count: int = 0,
        b_led_count: int = 0,
        delay: float = 0.002,
        max_rgb_value: int = 255,
    ):
        """
        Initialize BlinkStickPro class.

        @type r_led_count: int
        @param r_led_count: number of LEDs on R channel
        @type g_led_count: int
        @param g_led_count: number of LEDs on G channel
        @type b_led_count: int
        @param b_led_count: number of LEDs on B channel
        @type delay: int
        @param delay: default transmission delay between frames
        @type max_rgb_value: int
        @param max_rgb_value: maximum color value for RGB channels
        """

        self.r_led_count = r_led_count
        self.g_led_count = g_led_count
        self.b_led_count = b_led_count

        self.fps_count = -1

        self.data_transmission_delay = delay

        self.max_rgb_value = max_rgb_value

        # initialise data store for each channel
        # pre-populated with zeroes

        self.data = [[], [], []]

        for i in range(0, r_led_count):
            self.data[0].append([0, 0, 0])

        for i in range(0, g_led_count):
            self.data[1].append([0, 0, 0])

        for i in range(0, b_led_count):
            self.data[2].append([0, 0, 0])

        self.bstick = None

    def set_color(
        self,
        channel: int,
        index: int,
        r: int,
        g: int,
        b: int,
        remap_values: bool = True,
    ) -> None:
        """
        Set the color of a single pixel

        @type channel: int
        @param channel: R, G or B channel
        @type index: int
        @param index: the index of LED on the channel
        @type r: int
        @param r: red color byte
        @type g: int
        @param g: green color byte
        @type b: int
        @param b: blue color byte
        @type remap_values: bool
        @param remap_values: remap the values to maximum set in L{set_max_rgb_value}
        """

        if remap_values:
            r, g, b = [remap_color(val, self.max_rgb_value) for val in [r, g, b]]

        self.data[channel][index] = [g, r, b]

    def get_color(self, channel: int, index: int) -> tuple[int, int, int]:
        """
        Get the current color of a single pixel.

        @type  channel: int
        @param channel: the channel of the LED
        @type  index: int
        @param index: the index of the LED

        @rtype: (int, int, int)
        @return: 3-tuple for R, G and B values
        """

        val = self.data[channel][index]
        return val[1], val[0], val[2]

    def clear(self) -> None:
        """
        Set all pixels to black in the frame buffer.
        """
        for x in range(0, self.r_led_count):
            self.set_color(0, x, 0, 0, 0)

        for x in range(0, self.g_led_count):
            self.set_color(1, x, 0, 0, 0)

        for x in range(0, self.b_led_count):
            self.set_color(2, x, 0, 0, 0)

    def off(self) -> None:
        """
        Set all pixels to black in on the backend.
        """
        self.clear()
        self.send_data_all()

    def connect(self, serial: str | None = None):
        """
        Connect to the first BlinkStick found

        @type serial: str
        @param serial: Select the serial number of BlinkStick
        """

        if serial is None:
            self.bstick = find_first()
        else:
            self.bstick = find_by_serial(serial=serial)

        return self.bstick is not None

    def send_data(self, channel: int) -> None:
        """
        Send data stored in the internal buffer to the channel.

        @param channel:
            - 0 - R pin on BlinkStick Pro board
            - 1 - G pin on BlinkStick Pro board
            - 2 - B pin on BlinkStick Pro board
        """
        if self.bstick is None:
            return

        packet_data = [item for sublist in self.data[channel] for item in sublist]

        try:
            self.bstick.set_led_data(channel, packet_data)
            time.sleep(self.data_transmission_delay)
        except Exception as e:
            print("Exception: {0}".format(e))

    def send_data_all(self) -> None:
        """
        Send data to all channels
        """
        if self.r_led_count > 0:
            self.send_data(0)

        if self.g_led_count > 0:
            self.send_data(1)

        if self.b_led_count > 0:
            self.send_data(2)


class BlinkStickProMatrix(BlinkStickPro):
    """
    BlinkStickProMatrix class is specifically designed to control the individually
    addressable LEDs connected to the backend and arranged in a matrix. The tutorials section contains
    all the details on how to connect them to BlinkStick Pro with matrices.

    U{http://www.blinkstick.com/help/tutorials/blinkstick-pro-adafruit-neopixel-matrices}

    Code example on how you can use this class are available here:

    U{https://github.com/arvydas/blinkstick-python/wiki#code-examples-for-blinkstick-pro}

    Matrix is driven by using L{BlinkStickProMatrix.set_color} with [x,y] coordinates and class automatically
    divides data into subsets and sends it to the matrices.

    For example, if you have 2 8x8 matrices connected to BlinkStickPro and you initialize
    the class with

        >>> matrix = BlinkStickProMatrix(r_columns=8, r_rows=8, g_columns=8, g_rows=8)

    Then you can set the internal framebuffer by using {set_color} command:

        >>> matrix.set_color(x=10, y=5, r=255, g=0, b=0)
        >>> matrix.set_color(x=6, y=3, r=0, g=255, b=0)

    And send data to both matrices in one go:

        >>> matrix.send_data_all()

    """

    r_columns: int
    r_rows: int
    g_columns: int
    g_rows: int
    b_columns: int
    b_rows: int
    rows: int
    cols: int
    matrix_data: list[list[int]]

    def __init__(
        self,
        r_columns: int = 0,
        r_rows: int = 0,
        g_columns: int = 0,
        g_rows: int = 0,
        b_columns: int = 0,
        b_rows: int = 0,
        delay: float = 0.002,
        max_rgb_value: int = 255,
    ):
        """
        Initialize BlinkStickProMatrix class.

        @type r_columns: int
        @param r_columns: number of matric columns for R channel
        @type g_columns: int
        @param g_columns: number of matric columns for R channel
        @type b_columns: int
        @param b_columns: number of matric columns for R channel
        @type delay: int
        @param delay: default transmission delay between frames
        @type max_rgb_value: int
        @param max_rgb_value: maximum color value for RGB channels
        """
        r_leds = r_columns * r_rows
        g_leds = g_columns * g_rows
        b_leds = b_columns * b_rows

        self.r_columns = r_columns
        self.r_rows = r_rows
        self.g_columns = g_columns
        self.g_rows = g_rows
        self.b_columns = b_columns
        self.b_rows = b_rows

        super(BlinkStickProMatrix, self).__init__(
            r_led_count=r_leds,
            g_led_count=g_leds,
            b_led_count=b_leds,
            delay=delay,
            max_rgb_value=max_rgb_value,
        )

        self.rows = max(r_rows, g_rows, b_rows)
        self.cols = r_columns + g_columns + b_columns

        # initialise data store for matrix pre-populated with zeroes
        self.matrix_data = []

        for i in range(0, self.rows * self.cols):
            self.matrix_data.append([0, 0, 0])

    def set_color(
        self, x: int, y: int, r: int, g: int, b: int, remap_values: bool = True
    ) -> None:
        """
        Set the color of a single pixel in the internal framebuffer.

        @type x: int
        @param x: the x location in the matrix
        @type y: int
        @param y: the y location in the matrix
        @type r: int
        @param r: red color byte
        @type g: int
        @param g: green color byte
        @type b: int
        @param b: blue color byte
        @type remap_values: bool
        @param remap_values: Automatically remap values based on the {max_rgb_value} supplied in the constructor
        """

        if remap_values:
            r, g, b = [remap_color(val, self.max_rgb_value) for val in [r, g, b]]

        self.matrix_data[self._coord_to_index(x, y)] = [g, r, b]

    def _coord_to_index(self, x: int, y: int) -> int:
        return y * self.cols + x

    def get_color(self, x: int, y: int) -> tuple[int, int, int]:
        """
        Get the current color of a single pixel.

        @type  x: int
        @param x: x coordinate of the internal framebuffer
        @type  y: int
        @param y: y coordinate of the internal framebuffer

        @rtype: (int, int, int)
        @return: 3-tuple for R, G and B values
        """

        val = self.matrix_data[self._coord_to_index(x, y)]
        return val[1], val[0], val[2]

    def shift_left(self, remove: bool = False) -> None:
        """
        Shift all LED values in the matrix to the left

        @type remove: bool
        @param remove: whether to remove the pixels on the last column or move the to the first column
        """
        if not remove:
            temp = []
            for y in range(0, self.rows):
                temp.append(self.get_color(0, y))

        for y in range(0, self.rows):
            for x in range(0, self.cols - 1):
                r, g, b = self.get_color(x + 1, y)

                self.set_color(x, y, r, g, b, False)

        if remove:
            for y in range(0, self.rows):
                self.set_color(self.cols - 1, y, 0, 0, 0, False)
        else:
            for y in range(0, self.rows):
                col = temp[y]
                self.set_color(self.cols - 1, y, col[0], col[1], col[2], False)

    def shift_right(self, remove: bool = False) -> None:
        """
        Shift all LED values in the matrix to the right

        @type remove: bool
        @param remove: whether to remove the pixels on the last column or move the to the first column
        """

        if not remove:
            temp = []
            for y in range(0, self.rows):
                temp.append(self.get_color(self.cols - 1, y))

        for y in range(0, self.rows):
            for x in reversed(range(1, self.cols)):
                r, g, b = self.get_color(x - 1, y)

                self.set_color(x, y, r, g, b, False)

        if remove:
            for y in range(0, self.rows):
                self.set_color(0, y, 0, 0, 0, False)
        else:
            for y in range(0, self.rows):
                col = temp[y]
                self.set_color(0, y, col[0], col[1], col[2], False)

    def shift_down(self, remove: bool = False) -> None:
        """
        Shift all LED values in the matrix down

        @type remove: bool
        @param remove: whether to remove the pixels on the last column or move the to the first column
        """

        if not remove:
            temp = []
            for x in range(0, self.cols):
                temp.append(self.get_color(x, self.rows - 1))

        for y in reversed(range(1, self.rows)):
            for x in range(0, self.cols):
                r, g, b = self.get_color(x, y - 1)

                self.set_color(x, y, r, g, b, False)

        if remove:
            for x in range(0, self.cols):
                self.set_color(x, 0, 0, 0, 0, False)
        else:
            for x in range(0, self.cols):
                col = temp[x]
                self.set_color(x, 0, col[0], col[1], col[2], False)

    def shift_up(self, remove: bool = False):
        """
        Shift all LED values in the matrix up

        @type remove: bool
        @param remove: whether to remove the pixels on the last column or move the to the first column
        """

        if not remove:
            temp = []
            for x in range(0, self.cols):
                temp.append(self.get_color(x, 0))

        for x in range(0, self.cols):
            for y in range(0, self.rows - 1):
                r, g, b = self.get_color(x, y + 1)

                self.set_color(x, y, r, g, b, False)

        if remove:
            for x in range(0, self.cols):
                self.set_color(x, self.rows - 1, 0, 0, 0, False)
        else:
            for x in range(0, self.cols):
                col = temp[x]
                self.set_color(x, self.rows - 1, col[0], col[1], col[2], False)

    def number(self, x: int, y: int, n: int, r: int, g: int, b: int) -> None:
        """
        Render a 3x5 number n at location x,y and r,g,b color

        @type x: int
        @param x: the x location in the matrix (left of the number)
        @type y: int
        @param y: the y location in the matrix (top of the number)
        @type n: int
        @param n: number digit to render 0..9
        @type r: int
        @param r: red color byte
        @type g: int
        @param g: green color byte
        @type b: int
        @param b: blue color byte
        """
        if n == 0:
            self.rectangle(x, y, x + 2, y + 4, r, g, b)
        elif n == 1:
            self.line(x + 1, y, x + 1, y + 4, r, g, b)
            self.line(x, y + 4, x + 2, y + 4, r, g, b)
            self.set_color(x, y + 1, r, g, b)
        elif n == 2:
            self.line(x, y, x + 2, y, r, g, b)
            self.line(x, y + 2, x + 2, y + 2, r, g, b)
            self.line(x, y + 4, x + 2, y + 4, r, g, b)
            self.set_color(x + 2, y + 1, r, g, b)
            self.set_color(x, y + 3, r, g, b)
        elif n == 3:
            self.line(x, y, x + 2, y, r, g, b)
            self.line(x, y + 2, x + 2, y + 2, r, g, b)
            self.line(x, y + 4, x + 2, y + 4, r, g, b)
            self.set_color(x + 2, y + 1, r, g, b)
            self.set_color(x + 2, y + 3, r, g, b)
        elif n == 4:
            self.line(x, y, x, y + 2, r, g, b)
            self.line(x + 2, y, x + 2, y + 4, r, g, b)
            self.set_color(x + 1, y + 2, r, g, b)
        elif n == 5:
            self.line(x, y, x + 2, y, r, g, b)
            self.line(x, y + 2, x + 2, y + 2, r, g, b)
            self.line(x, y + 4, x + 2, y + 4, r, g, b)
            self.set_color(x, y + 1, r, g, b)
            self.set_color(x + 2, y + 3, r, g, b)
        elif n == 6:
            self.line(x, y, x + 2, y, r, g, b)
            self.line(x, y + 2, x + 2, y + 2, r, g, b)
            self.line(x, y + 4, x + 2, y + 4, r, g, b)
            self.set_color(x, y + 1, r, g, b)
            self.set_color(x + 2, y + 3, r, g, b)
            self.set_color(x, y + 3, r, g, b)
        elif n == 7:
            self.line(x + 1, y + 2, x + 1, y + 4, r, g, b)
            self.line(x, y, x + 2, y, r, g, b)
            self.set_color(x + 2, y + 1, r, g, b)
        elif n == 8:
            self.line(x, y, x + 2, y, r, g, b)
            self.line(x, y + 2, x + 2, y + 2, r, g, b)
            self.line(x, y + 4, x + 2, y + 4, r, g, b)
            self.set_color(x, y + 1, r, g, b)
            self.set_color(x + 2, y + 1, r, g, b)
            self.set_color(x + 2, y + 3, r, g, b)
            self.set_color(x, y + 3, r, g, b)
        elif n == 9:
            self.line(x, y, x + 2, y, r, g, b)
            self.line(x, y + 2, x + 2, y + 2, r, g, b)
            self.line(x, y + 4, x + 2, y + 4, r, g, b)
            self.set_color(x, y + 1, r, g, b)
            self.set_color(x + 2, y + 1, r, g, b)
            self.set_color(x + 2, y + 3, r, g, b)

    def rectangle(
        self, x1: int, y1: int, x2: int, y2: int, r: int, g: int, b: int
    ) -> None:
        """
        Draw a rectangle with it's corners at x1:y1 and x2:y2

        @type x1: int
        @param x1: the x1 location in the matrix for first corner of the rectangle
        @type y1: int
        @param y1: the y1 location in the matrix for first corner of the rectangle
        @type x2: int
        @param x2: the x2 location in the matrix for second corner of the rectangle
        @type y2: int
        @param y2: the y2 location in the matrix for second corner of the rectangle
        @type r: int
        @param r: red color byte
        @type g: int
        @param g: green color byte
        @type b: int
        @param b: blue color byte
        """

        self.line(x1, y1, x1, y2, r, g, b)
        self.line(x1, y1, x2, y1, r, g, b)
        self.line(x2, y1, x2, y2, r, g, b)
        self.line(x1, y2, x2, y2, r, g, b)

    def line(
        self, x1: int, y1: int, x2: int, y2: int, r: int, g: int, b: int
    ) -> list[tuple[int, int]]:
        """
        Draw a line from x1:y1 and x2:y2

        @type x1: int
        @param x1: the x1 location in the matrix for the start of the line
        @type y1: int
        @param y1: the y1 location in the matrix for the start of the line
        @type x2: int
        @param x2: the x2 location in the matrix for the end of the line
        @type y2: int
        @param y2: the y2 location in the matrix for the end of the line
        @type r: int
        @param r: red color byte
        @type g: int
        @param g: green color byte
        @type b: int
        @param b: blue color byte
        """
        points = []
        is_steep = abs(y2 - y1) > abs(x2 - x1)
        if is_steep:
            x1, y1 = y1, x1
            x2, y2 = y2, x2
        rev = False
        if x1 > x2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
            rev = True
        delta_x = x2 - x1
        delta_y = abs(y2 - y1)
        error = int(delta_x / 2)
        y = y1
        y_step = None

        if y1 < y2:
            y_step = 1
        else:
            y_step = -1
        for x in range(x1, x2 + 1):
            if is_steep:
                # print y, "~", x
                self.set_color(y, x, r, g, b)
                points.append((y, x))
            else:
                # print x, " ", y
                self.set_color(x, y, r, g, b)
                points.append((x, y))
            error -= delta_y
            if error < 0:
                y += y_step
                error += delta_x
                # Reverse the list if the coordinates were reversed
        if rev:
            points.reverse()
        return points

    def clear(self) -> None:
        """
        Set all pixels to black in the cached matrix
        """
        for y in range(0, self.rows):
            for x in range(0, self.cols):
                self.set_color(x, y, 0, 0, 0)

    def send_data(self, channel: int) -> None:
        """
        Send data stored in the internal buffer to the channel.

        @param channel:
            - 0 - R pin on BlinkStick Pro board
            - 1 - G pin on BlinkStick Pro board
            - 2 - B pin on BlinkStick Pro board
        """

        start_col = 0
        end_col = 0

        if channel == 0:
            start_col = 0
            end_col = self.r_columns

        if channel == 1:
            start_col = self.r_columns
            end_col = start_col + self.g_columns

        if channel == 2:
            start_col = self.r_columns + self.g_columns
            end_col = start_col + self.b_columns

        self.data[channel] = []

        # slice the huge array to individual packets
        for y in range(0, self.rows):
            start = y * self.cols + start_col
            end = y * self.cols + end_col

            self.data[channel].extend(self.matrix_data[start:end])

        super(BlinkStickProMatrix, self).send_data(channel)


def find_all() -> list[BlinkStick]:
    """
    Find all attached BlinkStick devices.

    @rtype: BlinkStick[]
    @return: a list of BlinkStick objects or None if no devices found
    """
    result: list[BlinkStick] = []
    if (found_devices := USBBackend.get_attached_blinkstick_devices()) is None:
        return result
    for d in found_devices:
        result.extend([BlinkStick(device=d)])

    return result


def find_first() -> BlinkStick | None:
    """
    Find first attached BlinkStick.

    @rtype: BlinkStick
    @return: BlinkStick object or None if no devices are found
    """
    blinkstick_devices = USBBackend.get_attached_blinkstick_devices(find_all=False)

    if blinkstick_devices:
        return BlinkStick(device=blinkstick_devices[0])

    return None


def find_by_serial(serial: str = "") -> BlinkStick | None:
    """
    Find BlinkStick backend based on serial number.

    @rtype: BlinkStick
    @return: BlinkStick object or None if no devices are found
    """

    devices = USBBackend.find_by_serial(serial=serial)

    if devices:
        return BlinkStick(device=devices[0])

    return None


def get_blinkstick_package_version() -> str:
    return version("blinkstick")
