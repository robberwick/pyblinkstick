from __future__ import annotations

import random
import re
from dataclasses import dataclass
from enum import Enum, auto

from blinkstick.exceptions import RGBColorException

HEX_COLOR_PATTERN = re.compile(r"^[0-9a-fA-F]{3}$|^[0-9a-fA-F]{6}$")


@dataclass()
class RGBColor:
    """
    Representation of an RGB color.

    This class provides functionality for manipulating RGB colors, including conversion between color
    representations (e.g., RGB to hex), color inversion, random color generation, and remapping color
    components to fit within a specified range. The class also ensures that RGB values remain within the
    valid range of 0 to 255.

    :ivar red: The red component of the color.
    :type red: int
    :ivar green: The green component of the color.
    :type green: int
    :ivar blue: The blue component of the color.
    :type blue: int
    """

    red: int = 0
    green: int = 0
    blue: int = 0

    def __post_init__(self):
        """
        Validates that the RGB color values are within the acceptable range (0-255)
        after the object is initialized. If not, raises an exception.

        :raises RGBColorException: If any of the red, green, or blue values are
            outside the range [0, 255].
        """

        if not all(0 <= value <= 255 for value in (self.red, self.green, self.blue)):
            raise RGBColorException("Color values must be between 0 and 255")

    @property
    def hex(self) -> str:
        """
        Converts RGB color representation to its hexadecimal string format.

        The method takes the `red`, `green`, and `blue` attributes of the object,
        formats them as two-digit hexadecimal numbers, and returns the concatenated
        hexadecimal color code prefixed with a `#`.

        :return: Hexadecimal representation of the RGB color.
        :rtype: str
        """
        return f"#{self.red:02x}{self.green:02x}{self.blue:02x}"

    def __iter__(self):
        """
        Provides an iterator over the color components of the object.

        This method enables the object to be an iterable, yielding its color components
        (red, green, and blue) in sequence.

        :return: Yields the red, green, and blue components of the object
        :rtype: iterator
        """
        yield self.red
        yield self.green
        yield self.blue

    def __invert__(self):
        """
        Inverts the RGB color values of the current instance, producing the complementary color.
        Each color channel (red, green, blue) is inverted by subtracting its value from 255.

        :return: A new `RGBColor` instance with inverted color channel values.
        :rtype: RGBColor
        """
        return RGBColor(
            red=255 - self.red,
            green=255 - self.green,
            blue=255 - self.blue,
        )

    @classmethod
    def from_hex(cls, hex_color: str) -> RGBColor:
        """
        Creates an instance of RGBColor from a hexadecimal color string.

        This method parses a hex color string, validates its format, and converts it
        into an RGB color representation. The input can be in either 3-character
        shorthand form (e.g., '#RGB') or 6-character form (e.g., '#RRGGBB'). It
        automatically handles the removal of the leading '#' character if present
        and expands shorthand notation to full 6-character representation before
        processing.

        :param hex_color: Hexadecimal color string to be converted. Must be a valid
            3-character (#RGB) or 6-character (#RRGGBB) hex color, optionally
            starting with '#'.
        :type hex_color: str

        :raises RGBColorException: If the input string does not conform to the 3
            or 6 character hexadecimal color format.

        :return: An instance of RGBColor initialized with the parsed RGB values
            (red, green, blue).
        :rtype: RGBColor
        """
        # Remove leading '#' if present
        if hex_color.startswith("#"):
            hex_color = hex_color[1:]
        # Validate with compiled regex - must be 3 or 6 hex characters
        if not HEX_COLOR_PATTERN.match(hex_color):
            raise RGBColorException(
                f"Invalid hex color: {hex_color}. Must be 3 or 6 hex characters."
            )
        # Expand shorthand form (#rgb to #rrggbb)
        if len(hex_color) == 3:
            hex_color = "".join(c + c for c in hex_color)

        return cls(
            red=int(hex_color[0:2], 16),
            green=int(hex_color[2:4], 16),
            blue=int(hex_color[4:6], 16),
        )

    @classmethod
    def random(cls) -> RGBColor:
        """
        Generates a new instance of the class with randomized RGB color values.

        This class method creates a color instance where each of the red, green,
        and blue components is assigned a random integer value between 0 and 255,
        inclusive. The method uses Python's `random.randint` function to ensure
        each component lies within the acceptable range for RGB colors.

        :return: A new instance of the class with randomized RGB components.
        :rtype: RGBColor
        """
        return cls(
            red=random.randint(0, 255),
            green=random.randint(0, 255),
            blue=random.randint(0, 255),
        )

    def remap_to_new_range(self, max_value: int) -> RGBColor:
        """
        Remaps the current RGB color components from their original range (0-255)
        to a new range (0 to `max_value`), ensuring that the result respects the
        defined range boundaries.

        :param max_value: The maximum value for the new range to which the RGB
            components will be remapped. Clamped between 0 and 255.
        :type max_value: int
        :raises ValueError: If the remapping calculations fail unexpectedly.
        :return: Returns a new RGBColor object with its red, green, and blue
            components remapped to the specified range.
        :rtype: RGBColor
        """

        # first clamp the new range between 0-255
        max_value = max(0, min(max_value, 255))

        def remap_component(value: int) -> int:
            # Convert from 0-255 range to 0-max_value range
            return int((value / 255.0) * max_value)

        return RGBColor(
            red=remap_component(self.red),
            green=remap_component(self.green),
            blue=remap_component(self.blue),
        )

    def packet_data(self) -> tuple[int, int, int]:
        """
        Retrieves the RGB packet data as a tuple.

        This method consolidates the red, green, and blue color component
        values into a single tuple. These values can represent colors in
        an RGB color model, commonly used in graphics, displays, and other
        visualization contexts.

        :return: A tuple containing the green, red, and blue color values
                 respectively.
        :rtype: tuple[int, int, int]
        """
        return self.green, self.red, self.blue


class NamedColor(Enum):
    ALICEBLUE = RGBColor(red=240, green=248, blue=255)
    ANTIQUEWHITE = RGBColor(red=250, green=235, blue=215)
    AQUA = RGBColor(red=0, green=255, blue=255)
    AQUAMARINE = RGBColor(red=127, green=255, blue=212)
    AZURE = RGBColor(red=240, green=255, blue=255)
    BEIGE = RGBColor(red=245, green=245, blue=220)
    BISQUE = RGBColor(red=255, green=228, blue=196)
    BLACK = RGBColor(red=0, green=0, blue=0)
    BLANCHEDALMOND = RGBColor(red=255, green=235, blue=205)
    BLUE = RGBColor(red=0, green=0, blue=255)
    BLUEVIOLET = RGBColor(red=138, green=43, blue=226)
    BROWN = RGBColor(red=165, green=42, blue=42)
    BURLYWOOD = RGBColor(red=222, green=184, blue=135)
    CADETBLUE = RGBColor(red=95, green=158, blue=160)
    CHARTREUSE = RGBColor(red=127, green=255, blue=0)
    CHOCOLATE = RGBColor(red=210, green=105, blue=30)
    CORAL = RGBColor(red=255, green=127, blue=80)
    CORNFLOWERBLUE = RGBColor(red=100, green=149, blue=237)
    CORNSILK = RGBColor(red=255, green=248, blue=220)
    CRIMSON = RGBColor(red=220, green=20, blue=60)
    CYAN = RGBColor(red=0, green=255, blue=255)
    DARKBLUE = RGBColor(red=0, green=0, blue=139)
    DARKCYAN = RGBColor(red=0, green=139, blue=139)
    DARKGOLDENROD = RGBColor(red=184, green=134, blue=11)
    DARKGRAY = RGBColor(red=169, green=169, blue=169)
    DARKGREY = RGBColor(red=169, green=169, blue=169)
    DARKGREEN = RGBColor(red=0, green=100, blue=0)
    DARKKHAKI = RGBColor(red=189, green=183, blue=107)
    DARKMAGENTA = RGBColor(red=139, green=0, blue=139)
    DARKOLIVEGREEN = RGBColor(red=85, green=107, blue=47)
    DARKORANGE = RGBColor(red=255, green=140, blue=0)
    DARKORCHID = RGBColor(red=153, green=50, blue=204)
    DARKRED = RGBColor(red=139, green=0, blue=0)
    DARKSALMON = RGBColor(red=233, green=150, blue=122)
    DARKSEAGREEN = RGBColor(red=143, green=188, blue=143)
    DARKSLATEBLUE = RGBColor(red=72, green=61, blue=139)
    DARKSLATEGRAY = RGBColor(red=47, green=79, blue=79)
    DARKSLATEGREY = RGBColor(red=47, green=79, blue=79)
    DARKTURQUOISE = RGBColor(red=0, green=206, blue=209)
    DARKVIOLET = RGBColor(red=148, green=0, blue=211)
    DEEPPINK = RGBColor(red=255, green=20, blue=147)
    DEEPSKYBLUE = RGBColor(red=0, green=191, blue=255)
    DIMGRAY = RGBColor(red=105, green=105, blue=105)
    DIMGREY = RGBColor(red=105, green=105, blue=105)
    DODGERBLUE = RGBColor(red=30, green=144, blue=255)
    FIREBRICK = RGBColor(red=178, green=34, blue=34)
    FLORALWHITE = RGBColor(red=255, green=250, blue=240)
    FORESTGREEN = RGBColor(red=34, green=139, blue=34)
    FUCHSIA = RGBColor(red=255, green=0, blue=255)
    GAINSBORO = RGBColor(red=220, green=220, blue=220)
    GHOSTWHITE = RGBColor(red=248, green=248, blue=255)
    GOLD = RGBColor(red=255, green=215, blue=0)
    GOLDENROD = RGBColor(red=218, green=165, blue=32)
    GRAY = RGBColor(red=128, green=128, blue=128)
    GREY = RGBColor(red=128, green=128, blue=128)
    GREEN = RGBColor(red=0, green=128, blue=0)
    GREENYELLOW = RGBColor(red=173, green=255, blue=47)
    HONEYDEW = RGBColor(red=240, green=255, blue=240)
    HOTPINK = RGBColor(red=255, green=105, blue=180)
    INDIANRED = RGBColor(red=205, green=92, blue=92)
    INDIGO = RGBColor(red=75, green=0, blue=130)
    IVORY = RGBColor(red=255, green=255, blue=240)
    KHAKI = RGBColor(red=240, green=230, blue=140)
    LAVENDER = RGBColor(red=230, green=230, blue=250)
    LAVENDERBLUSH = RGBColor(red=255, green=240, blue=245)
    LAWNGREEN = RGBColor(red=124, green=252, blue=0)
    LEMONCHIFFON = RGBColor(red=255, green=250, blue=205)
    LIGHTBLUE = RGBColor(red=173, green=216, blue=230)
    LIGHTCORAL = RGBColor(red=240, green=128, blue=128)
    LIGHTCYAN = RGBColor(red=224, green=255, blue=255)
    LIGHTGOLDENRODYELLOW = RGBColor(red=250, green=250, blue=210)
    LIGHTGRAY = RGBColor(red=211, green=211, blue=211)
    LIGHTGREY = RGBColor(red=211, green=211, blue=211)
    LIGHTGREEN = RGBColor(red=144, green=238, blue=144)
    LIGHTPINK = RGBColor(red=255, green=182, blue=193)
    LIGHTSALMON = RGBColor(red=255, green=160, blue=122)
    LIGHTSEAGREEN = RGBColor(red=32, green=178, blue=170)
    LIGHTSKYBLUE = RGBColor(red=135, green=206, blue=250)
    LIGHTSLATEGRAY = RGBColor(red=119, green=136, blue=153)
    LIGHTSLATEGREY = RGBColor(red=119, green=136, blue=153)
    LIGHTSTEELBLUE = RGBColor(red=176, green=196, blue=222)
    LIGHTYELLOW = RGBColor(red=255, green=255, blue=224)
    LIME = RGBColor(red=0, green=255, blue=0)
    LIMEGREEN = RGBColor(red=50, green=205, blue=50)
    LINEN = RGBColor(red=250, green=240, blue=230)
    MAGENTA = RGBColor(red=255, green=0, blue=255)
    MAROON = RGBColor(red=128, green=0, blue=0)
    MEDIUMAQUAMARINE = RGBColor(red=102, green=205, blue=170)
    MEDIUMBLUE = RGBColor(red=0, green=0, blue=205)
    MEDIUMORCHID = RGBColor(red=186, green=85, blue=211)
    MEDIUMPURPLE = RGBColor(red=147, green=112, blue=216)
    MEDIUMSEAGREEN = RGBColor(red=60, green=179, blue=113)
    MEDIUMSLATEBLUE = RGBColor(red=123, green=104, blue=238)
    MEDIUMSPRINGGREEN = RGBColor(red=0, green=250, blue=154)
    MEDIUMTURQUOISE = RGBColor(red=72, green=209, blue=204)
    MEDIUMVIOLETRED = RGBColor(red=199, green=21, blue=133)
    MIDNIGHTBLUE = RGBColor(red=25, green=25, blue=112)
    MINTCREAM = RGBColor(red=245, green=255, blue=250)
    MISTYROSE = RGBColor(red=255, green=228, blue=225)
    MOCCASIN = RGBColor(red=255, green=228, blue=181)
    NAVAJOWHITE = RGBColor(red=255, green=222, blue=173)
    NAVY = RGBColor(red=0, green=0, blue=128)
    OLDLACE = RGBColor(red=253, green=245, blue=230)
    OLIVE = RGBColor(red=128, green=128, blue=0)
    OLIVEDRAB = RGBColor(red=107, green=142, blue=35)
    ORANGE = RGBColor(red=255, green=165, blue=0)
    ORANGERED = RGBColor(red=255, green=69, blue=0)
    ORCHID = RGBColor(red=218, green=112, blue=214)
    PALEGOLDENROD = RGBColor(red=238, green=232, blue=170)
    PALEGREEN = RGBColor(red=152, green=251, blue=152)
    PALETURQUOISE = RGBColor(red=175, green=238, blue=238)
    PALEVIOLETRED = RGBColor(red=216, green=112, blue=147)
    PAPAYAWHIP = RGBColor(red=255, green=239, blue=213)
    PEACHPUFF = RGBColor(red=255, green=218, blue=185)
    PERU = RGBColor(red=205, green=133, blue=63)
    PINK = RGBColor(red=255, green=192, blue=203)
    PLUM = RGBColor(red=221, green=160, blue=221)
    POWDERBLUE = RGBColor(red=176, green=224, blue=230)
    PURPLE = RGBColor(red=128, green=0, blue=128)
    RED = RGBColor(red=255, green=0, blue=0)
    ROSYBROWN = RGBColor(red=188, green=143, blue=143)
    ROYALBLUE = RGBColor(red=65, green=105, blue=225)
    SADDLEBROWN = RGBColor(red=139, green=69, blue=19)
    SALMON = RGBColor(red=250, green=128, blue=114)
    SANDYBROWN = RGBColor(red=244, green=164, blue=96)
    SEAGREEN = RGBColor(red=46, green=139, blue=87)
    SEASHELL = RGBColor(red=255, green=245, blue=238)
    SIENNA = RGBColor(red=160, green=82, blue=45)
    SILVER = RGBColor(red=192, green=192, blue=192)
    SKYBLUE = RGBColor(red=135, green=206, blue=235)
    SLATEBLUE = RGBColor(red=106, green=90, blue=205)
    SLATEGRAY = RGBColor(red=112, green=128, blue=144)
    SLATEGREY = RGBColor(red=112, green=128, blue=144)
    SNOW = RGBColor(red=255, green=250, blue=250)
    SPRINGGREEN = RGBColor(red=0, green=255, blue=127)
    STEELBLUE = RGBColor(red=70, green=130, blue=180)
    TAN = RGBColor(red=210, green=180, blue=140)
    TEAL = RGBColor(red=0, green=128, blue=128)
    THISTLE = RGBColor(red=216, green=191, blue=216)
    TOMATO = RGBColor(red=255, green=99, blue=71)
    TURQUOISE = RGBColor(red=64, green=224, blue=208)
    VIOLET = RGBColor(red=238, green=130, blue=238)
    WHEAT = RGBColor(red=245, green=222, blue=179)
    WHITE = RGBColor(red=255, green=255, blue=255)
    WHITESMOKE = RGBColor(red=245, green=245, blue=245)
    YELLOW = RGBColor(red=255, green=255, blue=0)
    YELLOWGREEN = RGBColor(red=154, green=205, blue=50)

    @classmethod
    def from_name(cls, name) -> NamedColor:
        """
        Creates an instance of the class based on the provided name. The method attempts
        to map the given name to a corresponding enumeration value, ignoring case. If
        no match is found, an error is raised.

        :param name: The name of the color to map to an enumeration value. It is
            case-insensitive.
        :type name: str

        :raises ValueError: If the provided name does not correspond to any defined
            named color.

        :return: An instance of the class corresponding to the provided name.
        :rtype: NamedColor
        """
        try:
            return cls[name.upper()]
        except KeyError:
            raise ValueError(f"'{name}' is not defined as a named color.")
