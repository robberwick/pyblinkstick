"""
BlinkStick Pro client module for controlling advanced LED features.

This module provides classes for interfacing with BlinkStick Pro devices, particularly
focused on controlling individually addressable LEDs. The main components include:

- LEDChannel: Manages RGB color data for a single LED strip channel
- LEDDataFrame: Coordinates multiple LED channels for the BlinkStick Pro
- BlinkStickPro: Main client class for controlling BlinkStick Pro devices

The BlinkStickPro class supports features like:
- Individual LED control across multiple channels
- Different operating modes (single LED, inverse, WS2812)
- LED count configuration
- Data transmission with configurable delays
"""

from __future__ import annotations

import itertools
import time
from dataclasses import dataclass, field

from blinkstick.clients.base import BlinkStickClientBase
from blinkstick.colors import RGBColor, NamedColor
from blinkstick.devices import BlinkStickDevice
from blinkstick.enums import Channel, Mode
from blinkstick.utilities import convert_to_rgb_color


@dataclass
class LEDChannel:
    """Represents a channel of LEDs with functionality for managing pixel colors.

    This class models a channel of LEDs, allowing for individual pixel color
    manipulation, clearing all pixels, and preparing the channel's pixel data for
    transmission to an external LED device. The class ensures that pixel data is
    properly initialized and color values are managed according to the specified
    maximum RGB value.

    :ivar pixel_count: The number of pixels (LEDs) in the channel.
    :type pixel_count: int
    :ivar max_rgb_value: The maximum allowable RGB value for pixel colors.
    :type max_rgb_value: int
    :ivar pixel_data: A list of RGBColor objects representing the color data for
        each pixel.
    :type pixel_data: list[RGBColor]
    """

    pixel_count: int = 64
    max_rgb_value: int = 255
    pixel_data: list[RGBColor] = field(default_factory=list)

    def __post_init__(self):
        """
        Initialize or reset the pixel data after the object is created. This method is
        called automatically after the `__init__` method is executed to populate the
        `pixel_data` attribute with the default `RGBColor` instances based on the
        `pixel_count`.

        :return: None
        :rtype: None
        """
        self.pixel_data = [RGBColor() for _ in range(self.pixel_count)]

    def set_pixel(self, index: int, color: RGBColor | NamedColor | str) -> None:
        """
        Sets the color of a specific pixel in the pixel data.

        This function allows setting the color of a pixel at the given
        index using a specified color. The color can be provided either
        as an RGBColor object, a NamedColor instance, or a string. The
        provided color is internally converted to an RGBColor object
        and remapped to the current maximum RGB value range before
        being applied.

        :param index: The zero-based index of the pixel to set.
        :type index: int
        :param color: The color to assign to the pixel. Can be an `RGBColor`,
                      `NamedColor`, or a `str` representing a color.
        :type color: RGBColor | NamedColor | str
        :raises IndexError: If the provided index is out of the valid range
                            of pixel data.
        :raises ValueError: If the color string provided cannot be converted
                            into a recognized color format.
        :return: None
        :rtype: None
        """
        target_color = convert_to_rgb_color(color)
        self.pixel_data[index] = target_color.remap_to_new_range(
            max_value=self.max_rgb_value
        )

    def get_pixel(self, index: int) -> RGBColor:
        """
        Retrieves the RGB color of a pixel at the specified index.

        This method accesses the internal `pixel_data` list and fetches the RGB color
        data associated with the provided index. The `index` must be within the
        bounds of the list; otherwise, accessing an invalid index may raise an
        `IndexError`.

        :param index: The zero-based index of the pixel whose color needs to
            be retrieved.
        :type index: int

        :raises IndexError: If the `index` is out of range of the `pixel_data` list.

        :return: The RGB color at the specified index.
        :rtype: RGBColor
        """
        return self.pixel_data[index]

    def clear(self) -> None:
        """
        Clears the pixel data by resetting all pixels to their default RGBColor values.
        This method iterates over the entire pixel collection and assigns a new RGBColor
        object to each pixel, effectively resetting any custom color values. The pixel
        count remains unchanged.

        :return: None
        :rtype: None
        """
        self.pixel_data = [RGBColor() for _ in range(self.pixel_count)]

    def get_channel_packet_data(self) -> list[int]:
        """
        Generates a flattened list of packet data from the pixel data.

        The method iterates through all pixel data, retrieves their
        packet data, and concatenates the results into a single list.

        :return: A list containing combined packet data from all pixels
        :rtype: list[int]
        """
        return list(
            itertools.chain.from_iterable(
                pixel.packet_data() for pixel in self.pixel_data
            )
        )


@dataclass
class LEDDataFrame:
    """
    Represents a data frame for managing LED channels and their pixel data.

    This class provides mechanisms to manage RGB LED channels (red, green, and blue).
    Each channel is represented using the LEDChannel class, and the data frame allows
    for setting and retrieving pixel colors, clearing channels, and accessing channel-specific
    data. It maintains encapsulated methods to safely operate on the individual channels.

    :ivar red: Represents the red LED channel.
    :type red: LEDChannel
    :ivar green: Represents the green LED channel.
    :type green: LEDChannel
    :ivar blue: Represents the blue LED channel.
    :type blue: LEDChannel
    """

    red: LEDChannel = field(default_factory=LEDChannel)
    green: LEDChannel = field(default_factory=LEDChannel)
    blue: LEDChannel = field(default_factory=LEDChannel)

    def set_pixel_color(self, color: RGBColor, channel: Channel, index: int):
        """
        Sets the color of a specific pixel on the specified channel.

        This function utilizes the internal channel and pixel manipulation methods to
        precisely update the color of a pixel at a given index within a specified
        channel.

        :param color: The RGB color to set for the specified pixel
        :type color: RGBColor
        :param channel: The channel (or strip) where the pixel resides
        :type channel: Channel
        :param index: The index of the pixel to modify within the channel
        :type index: int
        :return: None
        :rtype: None
        """
        self._get_channel(channel).set_pixel(index, color)

    def _get_channel(self, channel):
        """
        Retrieves the target channel object based on the specified channel input.
        Raises an error if the provided channel does not match any valid option.

        :param channel: The channel to retrieve. Should be a value of the Channel
            enum (e.g., Channel.RED, Channel.GREEN, Channel.BLUE).
        :return: The target channel object corresponding to the input channel.
        :rtype: Any
        :raises ValueError: If the specified channel is not a valid option.
        """
        match channel:
            case Channel.RED:
                target_channel = self.red
            case Channel.GREEN:
                target_channel = self.green
            case Channel.BLUE:
                target_channel = self.blue
            case _:
                raise ValueError(f"Invalid channel: {channel}")
        return target_channel

    def get_pixel_color(self, channel: Channel, index: int) -> RGBColor:
        """
        Retrieves the color of a specific pixel from the given channel.

        This method accesses the specified channel, retrieves the pixel at the
        provided index, and returns its color information as an RGBColor object.

        :param channel: The channel from which to retrieve the pixel color.
        :type channel: Channel
        :param index: The index of the pixel within the specified channel.
        :type index: int
        :return: The RGB color information of the specified pixel.
        :rtype: RGBColor
        """
        target_channel = self._get_channel(channel)
        return target_channel.get_pixel(index)

    def clear(self):
        """
        Clears the contents of the red, green, and blue components. This method ensures
        that all three components are emptied of their current contents by invoking their
        respective `clear` methods.

        This function is typically used to reset or reinitialize the state of the color
        components to start afresh or remove previously stored values.

        :return: None
        :rtype: None
        """
        self.red.clear()
        self.green.clear()
        self.blue.clear()

    def get_channel_packet_data(self, channel: Channel) -> list[int]:
        """
        Retrieves the packet data associated with a specified communication channel.

        This function accesses the given channel object, retrieves its associated
        data, and returns it as a list of integers. It is used for extracting
        packet-related information from a specific channel instance.

        :param channel: The communication channel from which packet data is
            to be retrieved.
        :type channel: Channel
        :return: A list of integers representing the packet data for the
            specified channel.
        :rtype: list[int]
        """
        return self._get_channel(channel).get_channel_packet_data()


class BlinkStickPro(BlinkStickClientBase):
    """
    Represents a client to control BlinkStick Pro devices.

    This class provides an interface for managing and controlling BlinkStick Pro devices with
    multi-channel LED operations. It allows setting LED colors at specific pixels, managing device
    modes, sending data to LED channels, and other related operations. It also introduces features
    like error reporting, configurable data transmission delay, and LED brightness settings.

    :ivar data_transmission_delay: Specifies the delay in seconds between sending data
        packets to the BlinkStick device.
    :type data_transmission_delay: float
    :ivar dataframe: Represents the state of the LED data stored for the device. It stores
        colors for individual pixels in respective channels.
    :type dataframe: LEDDataFrame
    """

    data_transmission_delay: float
    dataframe: LEDDataFrame

    def __init__(
        self,
        device: BlinkStickDevice | None = None,
        error_reporting: bool = True,
        delay: float = 0.002,
        max_rgb_value: int = 255,
    ):
        """
        Initializes an instance of the class with the given parameters.

        The constructor initializes the LED data store, sets the delay for
        data transmission to the device, and specifies the maximum RGB value
        used for LED brightness. It also sets up the base class configuration
        for the BlinkStick device and error reporting.

        :param device: The BlinkStick device to be used. It allows control
            over the connected LED device. If set to None, it defaults to no
            specific device.
        :param error_reporting: A flag to enable or disable error reporting.
            If set to True, the system reports errors encountered during
            operations; otherwise, errors are suppressed.
        :param delay: The transmission delay in seconds between data sent to
            the BlinkStick device. It controls how fast or slow data is sent.
        :param max_rgb_value: The maximum allowed value for any RGB color
            component (Red, Green, Blue). It determines the maximum brightness
            that can be set for the LEDs.
        """

        super().__init__(device=device, error_reporting=error_reporting)

        # Initialise data store for LEDs
        self.dataframe = LEDDataFrame()

        self.data_transmission_delay = delay

        self.max_rgb_value = max_rgb_value

    def set_color_at_pixel(
        self,
        channel: Channel,
        index: int,
        color: RGBColor,
    ) -> None:
        """
        Sets the color of a specific pixel in the given channel.

        This method updates the color of a single pixel at a specific index within the
        specified channel to the provided RGB color value. It utilizes the internal
        dataframe to store the modified pixel color.

        :param channel: The channel where the pixel resides.
        :type channel: Channel
        :param index: The position of the pixel within the channel.
        :type index: int
        :param color: The RGBColor value to be set at the specified pixel.
        :type color: RGBColor
        :return: None
        """

        self.dataframe.set_pixel_color(color=color, channel=channel, index=index)

    def get_color_at_pixel(self, channel: Channel, index: int) -> RGBColor:
        """
        Retrieves the color of a specific pixel in the specified channel.

        This method accesses the pixel color data from a dataframe based on the
        given channel and index. It returns the RGBColor representation of the
        pixel at the specified location.

        :param channel: The channel from which to retrieve the pixel color.
        :type channel: Channel
        :param index: The index of the pixel within the channel.
        :type index: int
        :return: The RGBColor of the specified pixel.
        :rtype: RGBColor
        """

        return self.dataframe.get_pixel_color(channel=channel, index=index)

    def clear(self) -> None:
        """
        Clears all entries from the dataframe associated with the instance.

        This method removes all data stored in the dataframe, effectively
        resetting it to an empty state. Use this action carefully as it
        irreversibly deletes all current data from the dataframe.

        :return: None
        :rtype: None
        """
        self.dataframe.clear()

    def off(self) -> None:
        """
        Turns off the device by clearing its state and sending data to all relevant hardware.

        :return: Nothing is returned
        :rtype: None
        """
        self.clear()
        self.send_data_all()

    def send_data_to_channel(self, channel: Channel) -> None:
        """
        Sends data to the specified channel by extracting the packet data for that
        channel and transmitting it.

        This function retrieves the channel-specific packet data from the `dataframe`,
        sets the data on the LED for the channel, and introduces a transmission delay.
        If an exception occurs during the process, it is caught and output to the console.

        :param channel: The channel object to which the data will be transmitted.
        :type channel: Channel
        :return: No value is returned as the operation transmits data directly.
        :rtype: None
        :raises Exception: If any exception is encountered while setting LED data
            or during the transmission, it is caught and logged.
        """

        channel_packet_data = self.dataframe.get_channel_packet_data(channel=channel)

        try:
            self.set_led_data(channel, channel_packet_data)
            time.sleep(self.data_transmission_delay)
        except Exception as e:
            print("Exception: {0}".format(e))

    def send_data_all(self) -> None:
        """
        Sends data to all available channels: RED, GREEN, and BLUE.

        This method utilizes the send_data_to_channel function internally
        to send data to each of the defined channels. The main purpose of
        this function is to broadcast data to multiple channels sequentially.

        :return: None
        """
        self.send_data_to_channel(channel=Channel.RED)
        self.send_data_to_channel(channel=Channel.GREEN)
        self.send_data_to_channel(channel=Channel.BLUE)

    def set_mode(self, mode: int) -> None:
        """
        Sets the operational mode of the device by sending a control transfer
        command using the backend interface. The mode should be specified as
        an integer value corresponding to the desired configuration.

        :param mode: The integer value representing the desired operational
            mode of the device.
        :type mode: int
        :raises ValueError: If the input mode is outside the allowed range for
            the device.
        :raises CommunicationError: If the control transfer fails or encounters
            a communication error.
        :return: None
        :rtype: None
        """
        control_string = bytes(bytearray([4, mode]))

        self.backend.control_transfer(0x20, 0x9, 0x0004, 0, control_string)

    def get_mode(self) -> int:
        """
        Retrieve the operation mode of the device by performing a control transfer.

        The function sends a control transfer request to the device and retrieves
        the response data to determine the current operation mode. If the response
        contains the expected number of bytes, the second byte is interpreted as
        the mode. Otherwise, a default value (-1) is returned in case of an
        unexpected or error response.

        :raises ValueError: If the control transfer fails or returns an unexpected
            format, resulting in an invalid response.

        :return: The operation mode of the device as an integer. Returns -1 if the
            response is invalid or insufficient.
        :rtype: int
        """
        device_bytes = self.backend.control_transfer(0x80 | 0x20, 0x1, 0x0004, 0, 2)

        if len(device_bytes) >= 2:
            return device_bytes[1]
        else:
            return -1

    def set_led_count(self, count: int) -> None:
        """
        Sets the number of LEDs for supported devices.

        :param count: The number of LEDS for the device.
        :type count: int
        """
        control_string = bytes(bytearray([0x81, count]))

        self.backend.control_transfer(0x20, 0x9, 0x81, 0, control_string)

    def get_led_count(self) -> int:
        """
        Retrieves the LED count from the device.

        This method communicates with the device through a control transfer
        to retrieve the number of LEDs available. It processes the response
        to extract the LED count, ensuring a valid response is returned.
        If the received data does not meet the expected format, a default
        value indicating an error is returned.

        :raises RuntimeError: If there is an issue with communication or
            device response handling.
        :return: The count of LEDs reported by the device, or -1 if
            the response is invalid.
        :rtype: int
        """

        device_bytes = self.backend.control_transfer(0x80 | 0x20, 0x1, 0x81, 0, 2)

        if len(device_bytes) >= 2:
            return device_bytes[1]
        else:
            return -1

    @property
    def mode(self) -> Mode:
        """
        Fetch the current mode of the device

        :return: The mode of the device.
        :rtype: Mode
        """

        return self.backend.control_transfer(0x80 | 0x20, 0x1, 0x0004, 0, 2)[1]

    @mode.setter
    def mode(self, mode: Mode | int) -> None:
        """
        Sets the operational mode for the device. The mode can either be directly
        provided as an integer or as an instance of the `Mode` enum. If an enum
        is provided, its value will be extracted. Ensures that the mode value
        falls within the accepted range of the enum and constructs the control
        string accordingly before sending it to the device via a control transfer.

        :param mode: The desired operational mode. This can be an instance of the
                     `Mode` enum or an integer corresponding to the mode value.
        :type mode: Mode | int

        :raises ValueError: If the provided mode value is invalid.

        :return: None
        :rtype: None
        """
        # If mode is an enum, get the value
        # this will allow the user to pass in the enum directly, and also gate the value to the enum values
        if not isinstance(mode, int):
            mode = Mode(mode).value
        control_string = bytes(bytearray([4, mode]))

        self.backend.control_transfer(0x20, 0x9, 0x0004, 0, control_string)


# class BlinkStickProMatrix(BlinkStickPro):
#     """
#     BlinkStickProMatrix class is specifically designed to control the individually
#     addressable LEDs connected to the backend and arranged in a matrix. The tutorials section contains
#     all the details on how to connect them to BlinkStick Pro with matrices.
#
#     U{http://www.blinkstick.com/help/tutorials/blinkstick-pro-adafruit-neopixel-matrices}
#
#     Code example on how you can use this class are available here:
#
#     U{https://github.com/arvydas/blinkstick-python/wiki#code-examples-for-blinkstick-pro}
#
#     Matrix is driven by using L{BlinkStickProMatrix.set_color} with [x,y] coordinates and class automatically
#     divides data into subsets and sends it to the matrices.
#
#     For example, if you have 2 8x8 matrices connected to BlinkStickPro and you initialize
#     the class with
#
#         >>> matrix = BlinkStickProMatrix(r_columns=8, r_rows=8, g_columns=8, g_rows=8)
#
#     Then you can set the internal framebuffer by using {set_color} command:
#
#         >>> matrix.set_color(x=10, y=5, r=255, g=0, b=0)
#         >>> matrix.set_color(x=6, y=3, r=0, g=255, b=0)
#
#     And send data to both matrices in one go:
#
#         >>> matrix.send_data_all()
#
#     """
#
#     r_columns: int
#     r_rows: int
#     g_columns: int
#     g_rows: int
#     b_columns: int
#     b_rows: int
#     rows: int
#     cols: int
#     matrix_data: list[list[int]]
#
#     def __init__(
#         self,
#         r_columns: int = 0,
#         r_rows: int = 0,
#         g_columns: int = 0,
#         g_rows: int = 0,
#         b_columns: int = 0,
#         b_rows: int = 0,
#         delay: float = 0.002,
#         max_rgb_value: int = 255,
#     ):
#         """
#         Initialize BlinkStickProMatrix class.
#
#         @type r_columns: int
#         @param r_columns: number of matric columns for R channel
#         @type g_columns: int
#         @param g_columns: number of matric columns for R channel
#         @type b_columns: int
#         @param b_columns: number of matric columns for R channel
#         @type delay: int
#         @param delay: default transmission delay between frames
#         @type max_rgb_value: int
#         @param max_rgb_value: maximum color value for RGB channels
#         """
#         r_leds = r_columns * r_rows
#         g_leds = g_columns * g_rows
#         b_leds = b_columns * b_rows
#
#         self.r_columns = r_columns
#         self.r_rows = r_rows
#         self.g_columns = g_columns
#         self.g_rows = g_rows
#         self.b_columns = b_columns
#         self.b_rows = b_rows
#
#         super().__init__(
#             r_led_count=r_leds,
#             g_led_count=g_leds,
#             b_led_count=b_leds,
#             delay=delay,
#             max_rgb_value=max_rgb_value,
#         )
#
#         self.rows = max(r_rows, g_rows, b_rows)
#         self.cols = r_columns + g_columns + b_columns
#
#         # initialise data store for matrix pre-populated with zeroes
#         self.matrix_data = []
#
#         for i in range(0, self.rows * self.cols):
#             self.matrix_data.append([0, 0, 0])
#
#     def set_color(
#         self, x: int, y: int, r: int, g: int, b: int, remap_values: bool = True
#     ) -> None:
#         """
#         Set the color of a single pixel in the internal framebuffer.
#
#         @type x: int
#         @param x: the x location in the matrix
#         @type y: int
#         @param y: the y location in the matrix
#         @type r: int
#         @param r: red color byte
#         @type g: int
#         @param g: green color byte
#         @type b: int
#         @param b: blue color byte
#         @type remap_values: bool
#         @param remap_values: Automatically remap values based on the {max_rgb_value} supplied in the constructor
#         """
#
#         if remap_values:
#             r, g, b = [remap_color(val, self.max_rgb_value) for val in [r, g, b]]
#
#         self.matrix_data[self._coord_to_index(x, y)] = [g, r, b]
#
#     def _coord_to_index(self, x: int, y: int) -> int:
#         return y * self.cols + x
#
#     def get_color(self, x: int, y: int) -> tuple[int, int, int]:
#         """
#         Get the current color of a single pixel.
#
#         @type  x: int
#         @param x: x coordinate of the internal framebuffer
#         @type  y: int
#         @param y: y coordinate of the internal framebuffer
#
#         @rtype: (int, int, int)
#         @return: 3-tuple for R, G and B values
#         """
#
#         val = self.matrix_data[self._coord_to_index(x, y)]
#         return val[1], val[0], val[2]
#
#     def shift_left(self, remove: bool = False) -> None:
#         """
#         Shift all LED values in the matrix to the left
#
#         @type remove: bool
#         @param remove: whether to remove the pixels on the last column or move the to the first column
#         """
#         if not remove:
#             temp = []
#             for y in range(0, self.rows):
#                 temp.append(self.get_color(0, y))
#
#         for y in range(0, self.rows):
#             for x in range(0, self.cols - 1):
#                 r, g, b = self.get_color(x + 1, y)
#
#                 self.set_color(x, y, r, g, b, False)
#
#         if remove:
#             for y in range(0, self.rows):
#                 self.set_color(self.cols - 1, y, 0, 0, 0, False)
#         else:
#             for y in range(0, self.rows):
#                 col = temp[y]
#                 self.set_color(self.cols - 1, y, col[0], col[1], col[2], False)
#
#     def shift_right(self, remove: bool = False) -> None:
#         """
#         Shift all LED values in the matrix to the right
#
#         @type remove: bool
#         @param remove: whether to remove the pixels on the last column or move the to the first column
#         """
#
#         if not remove:
#             temp = []
#             for y in range(0, self.rows):
#                 temp.append(self.get_color(self.cols - 1, y))
#
#         for y in range(0, self.rows):
#             for x in reversed(range(1, self.cols)):
#                 r, g, b = self.get_color(x - 1, y)
#
#                 self.set_color(x, y, r, g, b, False)
#
#         if remove:
#             for y in range(0, self.rows):
#                 self.set_color(0, y, 0, 0, 0, False)
#         else:
#             for y in range(0, self.rows):
#                 col = temp[y]
#                 self.set_color(0, y, col[0], col[1], col[2], False)
#
#     def shift_down(self, remove: bool = False) -> None:
#         """
#         Shift all LED values in the matrix down
#
#         @type remove: bool
#         @param remove: whether to remove the pixels on the last column or move the to the first column
#         """
#
#         if not remove:
#             temp = []
#             for x in range(0, self.cols):
#                 temp.append(self.get_color(x, self.rows - 1))
#
#         for y in reversed(range(1, self.rows)):
#             for x in range(0, self.cols):
#                 r, g, b = self.get_color(x, y - 1)
#
#                 self.set_color(x, y, r, g, b, False)
#
#         if remove:
#             for x in range(0, self.cols):
#                 self.set_color(x, 0, 0, 0, 0, False)
#         else:
#             for x in range(0, self.cols):
#                 col = temp[x]
#                 self.set_color(x, 0, col[0], col[1], col[2], False)
#
#     def shift_up(self, remove: bool = False):
#         """
#         Shift all LED values in the matrix up
#
#         @type remove: bool
#         @param remove: whether to remove the pixels on the last column or move the to the first column
#         """
#
#         if not remove:
#             temp = []
#             for x in range(0, self.cols):
#                 temp.append(self.get_color(x, 0))
#
#         for x in range(0, self.cols):
#             for y in range(0, self.rows - 1):
#                 r, g, b = self.get_color(x, y + 1)
#
#                 self.set_color(x, y, r, g, b, False)
#
#         if remove:
#             for x in range(0, self.cols):
#                 self.set_color(x, self.rows - 1, 0, 0, 0, False)
#         else:
#             for x in range(0, self.cols):
#                 col = temp[x]
#                 self.set_color(x, self.rows - 1, col[0], col[1], col[2], False)
#
#     def number(self, x: int, y: int, n: int, r: int, g: int, b: int) -> None:
#         """
#         Render a 3x5 number n at location x,y and r,g,b color
#
#         @type x: int
#         @param x: the x location in the matrix (left of the number)
#         @type y: int
#         @param y: the y location in the matrix (top of the number)
#         @type n: int
#         @param n: number digit to render 0..9
#         @type r: int
#         @param r: red color byte
#         @type g: int
#         @param g: green color byte
#         @type b: int
#         @param b: blue color byte
#         """
#         if n == 0:
#             self.rectangle(x, y, x + 2, y + 4, r, g, b)
#         elif n == 1:
#             self.line(x + 1, y, x + 1, y + 4, r, g, b)
#             self.line(x, y + 4, x + 2, y + 4, r, g, b)
#             self.set_color(x, y + 1, r, g, b)
#         elif n == 2:
#             self.line(x, y, x + 2, y, r, g, b)
#             self.line(x, y + 2, x + 2, y + 2, r, g, b)
#             self.line(x, y + 4, x + 2, y + 4, r, g, b)
#             self.set_color(x + 2, y + 1, r, g, b)
#             self.set_color(x, y + 3, r, g, b)
#         elif n == 3:
#             self.line(x, y, x + 2, y, r, g, b)
#             self.line(x, y + 2, x + 2, y + 2, r, g, b)
#             self.line(x, y + 4, x + 2, y + 4, r, g, b)
#             self.set_color(x + 2, y + 1, r, g, b)
#             self.set_color(x + 2, y + 3, r, g, b)
#         elif n == 4:
#             self.line(x, y, x, y + 2, r, g, b)
#             self.line(x + 2, y, x + 2, y + 4, r, g, b)
#             self.set_color(x + 1, y + 2, r, g, b)
#         elif n == 5:
#             self.line(x, y, x + 2, y, r, g, b)
#             self.line(x, y + 2, x + 2, y + 2, r, g, b)
#             self.line(x, y + 4, x + 2, y + 4, r, g, b)
#             self.set_color(x, y + 1, r, g, b)
#             self.set_color(x + 2, y + 3, r, g, b)
#         elif n == 6:
#             self.line(x, y, x + 2, y, r, g, b)
#             self.line(x, y + 2, x + 2, y + 2, r, g, b)
#             self.line(x, y + 4, x + 2, y + 4, r, g, b)
#             self.set_color(x, y + 1, r, g, b)
#             self.set_color(x + 2, y + 3, r, g, b)
#             self.set_color(x, y + 3, r, g, b)
#         elif n == 7:
#             self.line(x + 1, y + 2, x + 1, y + 4, r, g, b)
#             self.line(x, y, x + 2, y, r, g, b)
#             self.set_color(x + 2, y + 1, r, g, b)
#         elif n == 8:
#             self.line(x, y, x + 2, y, r, g, b)
#             self.line(x, y + 2, x + 2, y + 2, r, g, b)
#             self.line(x, y + 4, x + 2, y + 4, r, g, b)
#             self.set_color(x, y + 1, r, g, b)
#             self.set_color(x + 2, y + 1, r, g, b)
#             self.set_color(x + 2, y + 3, r, g, b)
#             self.set_color(x, y + 3, r, g, b)
#         elif n == 9:
#             self.line(x, y, x + 2, y, r, g, b)
#             self.line(x, y + 2, x + 2, y + 2, r, g, b)
#             self.line(x, y + 4, x + 2, y + 4, r, g, b)
#             self.set_color(x, y + 1, r, g, b)
#             self.set_color(x + 2, y + 1, r, g, b)
#             self.set_color(x + 2, y + 3, r, g, b)
#
#     def rectangle(
#         self, x1: int, y1: int, x2: int, y2: int, r: int, g: int, b: int
#     ) -> None:
#         """
#         Draw a rectangle with it's corners at x1:y1 and x2:y2
#
#         @type x1: int
#         @param x1: the x1 location in the matrix for first corner of the rectangle
#         @type y1: int
#         @param y1: the y1 location in the matrix for first corner of the rectangle
#         @type x2: int
#         @param x2: the x2 location in the matrix for second corner of the rectangle
#         @type y2: int
#         @param y2: the y2 location in the matrix for second corner of the rectangle
#         @type r: int
#         @param r: red color byte
#         @type g: int
#         @param g: green color byte
#         @type b: int
#         @param b: blue color byte
#         """
#
#         self.line(x1, y1, x1, y2, r, g, b)
#         self.line(x1, y1, x2, y1, r, g, b)
#         self.line(x2, y1, x2, y2, r, g, b)
#         self.line(x1, y2, x2, y2, r, g, b)
#
#     def line(
#         self, x1: int, y1: int, x2: int, y2: int, r: int, g: int, b: int
#     ) -> list[tuple[int, int]]:
#         """
#         Draw a line from x1:y1 and x2:y2
#
#         @type x1: int
#         @param x1: the x1 location in the matrix for the start of the line
#         @type y1: int
#         @param y1: the y1 location in the matrix for the start of the line
#         @type x2: int
#         @param x2: the x2 location in the matrix for the end of the line
#         @type y2: int
#         @param y2: the y2 location in the matrix for the end of the line
#         @type r: int
#         @param r: red color byte
#         @type g: int
#         @param g: green color byte
#         @type b: int
#         @param b: blue color byte
#         """
#         points = []
#         is_steep = abs(y2 - y1) > abs(x2 - x1)
#         if is_steep:
#             x1, y1 = y1, x1
#             x2, y2 = y2, x2
#         rev = False
#         if x1 > x2:
#             x1, x2 = x2, x1
#             y1, y2 = y2, y1
#             rev = True
#         delta_x = x2 - x1
#         delta_y = abs(y2 - y1)
#         error = int(delta_x / 2)
#         y = y1
#         y_step = None
#
#         if y1 < y2:
#             y_step = 1
#         else:
#             y_step = -1
#         for x in range(x1, x2 + 1):
#             if is_steep:
#                 # print y, "~", x
#                 self.set_color(y, x, r, g, b)
#                 points.append((y, x))
#             else:
#                 # print x, " ", y
#                 self.set_color(x, y, r, g, b)
#                 points.append((x, y))
#             error -= delta_y
#             if error < 0:
#                 y += y_step
#                 error += delta_x
#                 # Reverse the list if the coordinates were reversed
#         if rev:
#             points.reverse()
#         return points
#
#     def clear(self) -> None:
#         """
#         Set all pixels to black in the cached matrix
#         """
#         for y in range(0, self.rows):
#             for x in range(0, self.cols):
#                 self.set_color(x, y, 0, 0, 0)
#
#     def send_data(self, channel: int) -> None:
#         """
#         Send data stored in the internal buffer to the channel.
#
#         @param channel:
#             - 0 - R pin on BlinkStick Pro board
#             - 1 - G pin on BlinkStick Pro board
#             - 2 - B pin on BlinkStick Pro board
#         """
#
#         start_col = 0
#         end_col = 0
#
#         if channel == 0:
#             start_col = 0
#             end_col = self.r_columns
#
#         if channel == 1:
#             start_col = self.r_columns
#             end_col = start_col + self.g_columns
#
#         if channel == 2:
#             start_col = self.r_columns + self.g_columns
#             end_col = start_col + self.b_columns
#
#         self.data[channel] = []
#
#         # slice the huge array to individual packets
#         for y in range(0, self.rows):
#             start = y * self.cols + start_col
#             end = y * self.cols + end_col
#
#             self.data[channel].extend(self.matrix_data[start:end])
#
#         super(BlinkStickProMatrix, self).send_data(channel)
