from importlib.metadata import version, PackageNotFoundError

from blinkstick.clients import BlinkStick
from .colors import NamedColor
from .core import find_all, find_first, find_by_serial, get_blinkstick_package_version
from .enums import BlinkStickVariant
from .exceptions import BlinkStickException

try:
    __version__ = version("blinkstick")
except PackageNotFoundError:
    __version__ = "BlinkStick package not installed"
