"""
Base module providing core functionality for BlinkStick device control.

This module implements abstract base functionality for BlinkStick devices and should not
be instantiated directly. Instead, use the appropriate concrete implementation:
- BlinkStickPro for Pro devices
- BlinkStick for standard devices

The base module provides:
- Common USB communication infrastructure
- Core LED control and state management
- Animation support (morphing, blinking, pulsing)
- Device information and configuration access
- Cross-platform backend handling (Windows/Unix)

For direct device control, import and use the appropriate client implementation
from the blinkstick.clients package instead of this base module.
"""

from __future__ import annotations

import sys
from abc import ABC

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
from blinkstick.utilities import (
    string_to_info_block_data,
    convert_to_rgb_color,
    determine_report_id,
)

if sys.platform == "win32":
    from blinkstick.backends.win32 import Win32Backend as USBBackend
else:
    from blinkstick.backends.unix_like import UnixLikeBackend as USBBackend


class BlinkStickClientBase(ABC):
    """
    Represents a base class for BlinkStick LED management, providing interfaces to interact
    with the underlying USB-based backend for LED control and data communication.

    This class is abstract and serves as the foundation for managing BlinkStick devices.
    It offers methods for LED color manipulation, retrieving device information, and handling
    multiple channels and configurations. Subclasses may extend it to implement variant-specific
    features or behaviors.

    :ivar _inverse: Indicates whether inverse mode is enabled for colors.
    :type _inverse: bool
    :ivar _error_reporting: Determines whether errors are reported when interacting with the backend.
    :type _error_reporting: bool
    :ivar _max_rgb_value: The maximum allowable RGB value for color settings.
    :type _max_rgb_value: int
    :ivar backend: Represents the USB backend for communicating with the BlinkStick device.
    :type backend: USBBackend
    """

    _inverse: bool
    _error_reporting = True
    _max_rgb_value: int

    backend: USBBackend

    def __init__(
        self, device: BlinkStickDevice | None = None, error_reporting: bool = True
    ):
        """
        Initializes the object with a specified device and error reporting setting. This
        constructor sets the necessary default attributes, including error reporting,
        maximum RGB value, and inversion setting. It also initializes an Animator object
        linked to the instance and, if a device is provided, establishes a USB backend
        for communication.

        :param device: The BlinkStickDevice instance to be used for USB communication.
                        If not provided, the backend won't be initialized, defaults to None
        :type device: BlinkStickDevice, optional
        :param error_reporting: Indicates whether error reporting should be enabled,
                                defaults to True
        :type error_reporting: bool
        """
        self._error_reporting = error_reporting
        self._max_rgb_value = 255
        self._inverse = False
        self.animator = Animator(self)

        if device:
            self.backend = USBBackend(device)

    def __getattribute__(self, name):
        """
        Overrides the default behavior of the __getattribute__ method to incorporate
        custom logic for callable attributes. Specifically, it wraps callable attributes
        with additional checks that raise an exception if a "backend" attribute is not set.
        This is bypassed for callable attributes marked with the "no_backend_required"
        flag or for certain special methods like __repr__ and __str__.

        :param name: The name of the attribute to retrieve.
        :type name: str

        :raises NotConnected: Raised when trying to access a callable attribute
            that requires a backend while no backend is set.

        :return: The requested attribute, either as-is or wrapped with the custom
            check logic if it is callable and requires a backend.
        :rtype: Any
        """
        # Bypass wrapper logic for special methods like __repr__, __str__, etc.
        attr = object.__getattribute__(self, name)

        if callable(attr) and not getattr(attr, "no_backend_required", False):
            from functools import wraps

            @wraps(attr)
            def wrapper(*args, **kwargs):
                if not getattr(self, "backend", None):
                    raise NotConnected("No backend set")
                return attr(*args, **kwargs)

            return wrapper
        return attr

    def __repr__(self):
        """
        Provides a string representation of the object, including its variant description
        and serial number if connected. If the object is not connected, a default string
        indicating disconnection is returned.

        :raises NotConnected: If the object is not connected when attempting to access
            the `serial` or `variant` attributes.

        :return: A string containing the representation of the object, including variant
            and serial if connected, or a default string if not connected.
        :rtype: str
        """
        try:
            serial = self.serial
            variant = self.variant.description
        except NotConnected:
            return "<BlinkStick: Not connected>"
        return f"<{self.__class__.__name__}: Variant={variant} Serial={serial}>"

    def __str__(self):
        """
        Generate a string representation of the Blinkstick device.

        Attempts to retrieve the serial number and description of the variant associated
        with the device. If the device is not connected, an appropriate message is returned.

        :raises NotConnected: Raised when the device is not connected, preventing access
                              to its serial number or variant description.
        :return: A string representing the Blinkstick device, including its variant
                 description and serial number if connected, or a message indicating that
                 it is not connected.
        :rtype: str
        """
        try:
            serial = self.serial
            variant = self.variant.description
        except NotConnected:
            return "Blinkstick - Not connected"
        return f"{variant} ({serial})"

    @property
    def serial(self) -> str:
        """
        Provides the serial number of a device or system.

        The `serial` property retrieves the serial number from the `backend` object
        and returns it as a string.

        ::

            BSnnnnnn-1.0
            ||  |    | |- Software minor version
            ||  |    |--- Software major version
            ||  |-------- Denotes sequential number
            ||----------- Denotes BlinkStick backend

        Software version defines the capabilities of the backend

        :return: Serial number of the device or system
        :rtype: str
        """
        return self.backend.get_serial()

    @property
    def manufacturer(self) -> str:
        """
        Gets the manufacturer information from the backend.

        :return: The manufacturer's name.
        :rtype: str
        """
        return self.backend.get_manufacturer()

    @property
    def variant(self) -> BlinkStickVariant:
        """
        Retrieves the product variant of the BlinkStick device.

        :return: The variant of the BlinkStick device.
        :rtype: BlinkStickVariant
        """

        return self.backend.get_variant()

    @property
    def variant_string(self) -> str:
        """
        Returns the description of the variant.

        :return: The description of the variant.
        :rtype: str
        """
        return self.variant.description

    @property
    def description(self) -> str:
        """
        Gets the description of the device.

        :return: The description of the device
        :rtype: str
        """
        return self.backend.get_description()

    @property
    def error_reporting(self) -> bool:
        """
        Gets the value indicating whether error reporting is enabled.

        This property returns the status of error reporting, where `True` indicates
        that error reporting is enabled, and `False` indicates it is disabled. This
        can be useful for enabling or disabling error reporting dynamically based
        on application settings or runtime conditions.

        :return: The status of error reporting.
        :rtype: bool
        """
        return self._error_reporting

    @error_reporting.setter
    def error_reporting(self, error_reporting: bool) -> None:
        """
        Sets the error reporting configuration for the instance.

        :param error_reporting: A boolean value indicating whether error reporting is enabled or
            disabled.
        :type error_reporting: bool
        """
        self._error_reporting = error_reporting

    def set_color(
        self,
        color: RGBColor | NamedColor | str,
        channel: Channel = Channel.RED,
        index: int = 0,
    ) -> None:
        """
        Set the color for a specific channel and index.

        This function sets the target color for the specified channel and index using
        the provided color. The color can be provided as an RGBColor, NamedColor, or
        a string. If inverse mode is enabled, the color will be inverted before being
        set. The function prepares a control string based on the specified channel
        and index and sends it via the backend's control transfer. If error reporting
        is enabled, exceptions are raised on failure. Otherwise, exceptions are silently
        ignored.

        :param color: The target color to set, which can be specified as an instance
            of RGBColor, NamedColor, or a string.
        :type color: RGBColor | NamedColor | str
        :param channel: The channel to be updated, defaults to Channel.RED.
        :type channel: Channel, optional
        :param index: The index of the light/pixel to update, defaults to 0.
        :type index: int, optional
        :raises ValueError: If an invalid color is provided or cannot be converted to
            RGBColor.
        :raises SomeBackendException: If the backend control transfer fails and error
            reporting is enabled.
        :return: None
        :rtype: None
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
        """
        Retrieves the RGB color value for the specified LED index from the device.

        The method fetches the raw color data either through a control transfer
        or by obtaining the LED-specific data for non-zero indices. If the `_inverse`
        flag is set, the color values are inverted.

        :param index: LED index for which the RGB color needs to be retrieved. Defaults to 0.
        :type index: int, optional
        :raises IndexError: Raised if the LED data retrieval encounters an
            invalid index or processing error.
        :return: The RGB color representation for the specified LED index.
        :rtype: RGBColor
        """
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
        """
        Retrieve the hexadecimal color code for a specified index.

        This method fetches a color based on the given index using the
        `_get_color` method and returns its hexadecimal representation.

        :param index: The index of the color to retrieve, defaults to 0
        :type index: int, optional
        :return: The hexadecimal representation of the color
        :rtype: str
        """
        return self._get_color(index=index).hex

    def get_color(
        self,
        index: int = 0,
    ) -> RGBColor:
        """
        Retrieves the color associated with the provided index.

        The method returns an RGB color based on the passed index. It uses the
        underlying `_get_color` method of the class to fetch the color value.
        If no index is provided, it defaults to 0.

        :param index: The index of the color to retrieve, defaults to 0
        :type index: int, optional
        :raises ValueError: If the index is out of bounds or invalid
        :return: The RGB color associated with the provided index
        :rtype: RGBColor
        """

        return self._get_color(index=index)

    def set_led_data(self, channel: Channel, data: list[int]) -> None:
        """
        Sets the LED data for a given channel. This involves creating a report based
        on the input data and sending it via the control transfer to the backend. Each
        subsequent LED value is padded with zeroes if the input data does not fill the
        expected length of the report.

        :param channel: The channel to which the LED data should be applied. Determines
            which part of the device configuration will be updated.
        :type channel: Channel
        :param data: A list of integer values representing the LED configurations. The
            list size may be smaller than the maximum LEDs allowed, and will be padded
            with zeroes if needed.
        :type data: list[int]
        :return: None
        :rtype: None
        """

        report_id, max_leds = determine_report_id(len(data))

        report = [0, channel]

        for i in range(0, max_leds * 3):
            if len(data) > i:
                report.append(data[i])
            else:
                report.append(0)

        self.backend.control_transfer(0x20, 0x9, report_id, 0, bytes(bytearray(report)))

    def get_led_data(self, count: int) -> list[int]:
        """
        Fetches LED data from a device based on the specified count. The function determines the
        appropriate report ID and maximum number of LEDs. It then retrieves the LED data using
        a control transfer operation.

        :param count: The number of LEDs to fetch data for.
        :type count: int

        :raises ValueError: If the count is invalid or exceeds the hardware's capacity.
        :raises IOError: If there is a failure in accessing the device.
        :raises RuntimeError: If the backend fails to retrieve the data.

        :return: A list of integers representing the LED data.
        :rtype: list[int]
        """

        report_id, max_leds = determine_report_id(count)

        device_bytes = self.backend.control_transfer(
            0x80 | 0x20, 0x1, report_id, 0, max_leds * 3 + 2
        )

        return device_bytes[2 : 2 + count * 3]

    @property
    def mode(self) -> Mode:
        """
        Returns the current operational mode of the object.

        :raises NotImplementedError: Raised when mode switching is not supported
            for the specific variant of the object.
        :return: The operational mode of the object.
        :rtype: Mode
        """
        raise NotImplementedError(
            f"Mode switching is not supported for {self.variant_string}"
        )

    @mode.setter
    def mode(self, value) -> Mode:
        """
        Raises a `NotImplementedError` when attempting to set a new mode for the instance.
        This indicates that mode switching is not supported for the current variant.

        :param value: The mode to be set for the instance.
        :type value: Mode
        :raises NotImplementedError: Indicates that mode switching is not supported for the
            specific variant of the instance.
        :return: The mode object after attempting to set it.
        :rtype: Mode
        """
        raise NotImplementedError(
            f"Mode switching is not supported for {self.variant_string}"
        )

    @property
    def led_count(self) -> int:
        """
        Provides the count of LEDs available on the device. This information is
        retrieved through a control transfer operation with the backend.

        :raises ValueError: If the control transfer operation returns an unexpected
            response or invalid data format.

        :return: The number of LEDs available, as determined by the device response.
            Returns -1 if the response from the device is invalid or insufficient.
        :rtype: int
        """

        device_bytes = self.backend.control_transfer(0x80 | 0x20, 0x1, 0x81, 0, 2)

        if len(device_bytes) >= 2:
            return device_bytes[1]
        else:
            return -1

    @led_count.setter
    def led_count(self, count: int) -> None:
        """
        Sets the number of LEDs to control on the device by sending a control
        transfer command via the backend. The number of LEDs is determined by
        the `count` parameter.

        :param count: Number of LEDs to control on the device.
        :type count: int
        :raises ValueError: If the control transfer command fails or the `count`
            exceeds the allowed limit for the device.
        """
        control_string = bytes(bytearray([0x81, count]))

        self.backend.control_transfer(0x20, 0x9, 0x81, 0, control_string)

    @property
    def info_block1(self) -> str:
        """
        Returns the contents of info block 1 on the device.
        This is a 32 byte array that can contain any data. It's supposed to
        hold the "Name" of the backend making it easier to identify rather than
        a serial number.

        :raises ValueError: If the control transfer fails, an invalid response is received, or the
            extracted string is not properly null-terminated.

        :return: Decoded and formatted string extracted from the device response.
        :rtype: str
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
        Sets the value of the info_block1 property by transferring the provided data to the
        underlying backend control device. The data is first converted to the required format
        using the `string_to_info_block_data` function before being sent.

        :param data: The new value to set for the info_block1 property. It must be a string
                     formatted appropriately for the targeted device.
        :type data: str

        :raises ValueError: Raised if the provided data does not meet the required format.
        """
        self.backend.control_transfer(
            0x20, 0x9, 0x0002, 0, string_to_info_block_data(data)
        )

    @property
    def info_block2(self) -> str:
        """
        Returns the contents of info block 2 on the device.
        This is a 32 byte array that can contain any data. It's supposed to
        hold the "Name" of the backend making it easier to identify rather than
        a serial number.

        :raises ValueError: If the control transfer fails, an invalid response is received, or the
            extracted string is not properly null-terminated.

        :return: Decoded and formatted string extracted from the device response.
        :rtype: str
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
        Sets the value of the `info_block2` attribute with the provided data. Converts the
        input string data into the appropriate formatted block data and updates it
        via a control transfer operation using the backend interface.

        :param data: The string data to be written to `info_block2` in the
            expected info block format.
        :type data: str
        """
        self.backend.control_transfer(
            0x20, 0x9, 0x0003, 0, string_to_info_block_data(data)
        )

    def set_random_color(self) -> None:
        """
        Sets the color to a random value by invoking the `set_color`
        method with the argument "random".

        :return: None
        :rtype: None
        """
        self.set_color("random")

    def turn_off(self) -> None:
        """
        Turns off the LED by changing its color to black.

        This function sets the color of the LED to black, effectively
        turning it off. It makes use of the `set_color` method to apply the change.

        :return: None
        :rtype: NoneType
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
        Morphs the color of a specific channel or LED index to a target color
        over a specified duration and number of steps. This method allows for
        smooth color transitions, optionally executing the animation
        immediately or queuing it for later execution.

        :param color: Target color to morph to. Can be an instance of RGBColor,
            NamedColor, or a string representation of the color.
        :param channel: LED channel to apply the morph animation to, defaults
            to Channel.RED
        :type channel: Channel, optional
        :param index: Specific LED index to target within the selected channel,
            defaults to 0
        :type index: int, optional
        :param duration: Total duration of the morph animation in milliseconds,
            defaults to 1000
        :type duration: int, optional
        :param steps: Number of intermediate steps in the animation for a
            smoother transition, defaults to 50
        :type steps: int, optional
        :param immediate: Determines whether to immediately execute the animation
            or queue it for later. If True, the animation executes immediately,
            otherwise it is queued, defaults to False
        :type immediate: bool, optional
        :return: None
        :rtype: None
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
        Blink the light in the specified color, on a given channel and index, with the
        specified repeat count and delay between blinks.

        The blink function creates a blink animation based on the provided parameters.
        This animation can either be queued to run later or executed immediately, depending
        on the `immediate` parameter.

        :param color: The color to blink, can be an RGBColor, NamedColor, or string.
        :type color: RGBColor | NamedColor | str
        :param channel: The channel to apply the blink animation on, defaults to Channel.RED.
        :type channel: Channel, optional
        :param index: The index of the light to blink, defaults to 0.
        :type index: int, optional
        :param repeats: The number of times to repeat the blink animation, defaults to 1.
        :type repeats: int, optional
        :param delay: The delay between each blink in milliseconds, defaults to 500.
        :type delay: int, optional
        :param immediate: Whether to play the animation immediately instead of queuing it,
            defaults to False.
        :type immediate: bool, optional
        :return: None
        :rtype: None
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
        Triggers a pulse animation on an LED or group of LEDs. The pulse animation transitions
        the light's intensity smoothly from off to the specified color and back to off.

        :param color: The target color for the pulse animation. Can be an RGBColor object,
                      a NamedColor, or a string representing the color.
        :param channel: The LED channel to use for the animation. Defaults to Channel.RED.
        :param index: The specific index of the LED within the channel to apply the animation.
                      Defaults to 0.
        :param repeats: The number of times the pulse animation should repeat. Defaults to 1.
        :param duration: The total duration of the pulse animation in milliseconds. Defaults
                         to 1000.
        :param steps: The number of discrete steps used during the pulse transition. Higher
                      numbers yield smoother animations. Defaults to 50.
        :param immediate: If True, the animation will play immediately and interrupts other
                          animations. If False, it will queue the animation. Defaults to False.

        :return: This function does not return a value.
        :rtype: None
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
        """
        Stops all ongoing animations controlled by the animator instance.

        This method ensures that any active animations are halted and that the
        state of the animator is reset to a non-active state.

        :return: None
        :rtype: None
        """
        self.animator.stop()

    @property
    def inverse(self) -> bool:
        """
        Returns whether the device is in inverse mode.

        :return: Device inverse mode status. True if in inverse mode, False otherwise.
        :rtype: bool
        """
        return self._inverse

    @inverse.setter
    def inverse(self, value: bool) -> None:
        """
        Sets the value for the 'inverse' property.

        This method sets the value of the '_inverse' attribute. If the input
        value is of type string, it is converted to lowercase and checked
        against the string "true" to determine its boolean equivalent. The
        final value is stored as a boolean.

        :param value: The value to set for the 'inverse' property. If it is
            a string, it will be interpreted as a boolean based on its
            content ("true" is evaluated as True, case-insensitive). For
            other types, it is cast to a boolean.
        :type value: bool or str
        """
        if type(value) is str:
            value = value.lower() == "true"  # type: ignore
        self._inverse = bool(value)

    @property
    def max_rgb_value(self) -> int:
        """
        Returns the currently set maximum RGB value for the object.

        :return: The maximum RGB value.
        :rtype: int
        """
        return self._max_rgb_value

    @max_rgb_value.setter
    def max_rgb_value(self, value: int) -> None:
        """
        Set the maximum RGB value for the color, ensuring it is clamped within the valid range of 0 to 255.

        :param value: The new maximum RGB value to be set. It should be an integer and will be clamped
                      to the range 0 to 255.
        :type value: int
        """
        # convert to int and clamp to 0..255
        # TODO remap current color immediately
        value = max(0, min(255, int(value)))
        self._max_rgb_value = value
