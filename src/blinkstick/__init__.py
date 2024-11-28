from importlib.metadata import version, PackageNotFoundError

from blinkstick.clients.blinkstick import BlinkStick, BlinkStickPro, BlinkStickProMatrix
from blinkstick.clients.blinkstick import (
    find_all,
    find_by_serial,
    find_first,
    get_blinkstick_package_version,
)
from .colors import Color, ColorFormat
from .constants import BlinkStickVariant
from .exceptions import BlinkStickException

try:
    __version__ = version("blinkstick")
except PackageNotFoundError:
    __version__ = "BlinkStick package not installed"
