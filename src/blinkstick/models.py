import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class SerialDetails:
    """
    A BlinkStick serial number representation.

        BSnnnnnn-1.0
        ||  |    | |- Software minor version
        ||  |    |--- Software major version
        ||  |-------- Denotes sequential number
        ||----------- Denotes BlinkStick backend


    """

    serial: str
    major_version: int = field(init=False)
    minor_version: int = field(init=False)
    sequence_number: int = field(init=False)

    def __post_init__(self):
        serial_number_regex = r"BS(\d+)-(\d+)\.(\d+)"
        match = re.match(serial_number_regex, self.serial)
        if not match:
            raise ValueError(f"Invalid serial number: {self.serial}")

        object.__setattr__(self, "sequence_number", int(match.group(1)))
        object.__setattr__(self, "major_version", int(match.group(2)))
        object.__setattr__(self, "minor_version", int(match.group(3)))


@dataclass()
class Color:
    """
    A color representation.

    :param red: Red component of the color (0-255)
    :param green: Green component of the color (0-255)
    :param blue: Blue component of the color (0-255)
    """

    red: int = 0
    green: int = 0
    blue: int = 0

    def __post_init__(self):
        if not all(0 <= value <= 255 for value in (self.red, self.green, self.blue)):
            raise ValueError("Color values must be between 0 and 255")

    def __iter__(self):
        """
        Iterate over the color components.
        """
        yield self.red
        yield self.green
        yield self.blue
