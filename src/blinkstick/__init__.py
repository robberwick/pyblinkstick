"""
The BlinkStick package provides a Python interface for controlling BlinkStick USB LED devices.

This package includes:
- Device discovery and connection management
- RGB and named color support
- Animation system for creating dynamic lighting effects
- Support for different BlinkStick variants and channels

Main Components:
- clients: Different client implementations for BlinkStick device control
- colors: Color management with RGB and named color support
- animation: Framework for creating and managing LED animations
- core: Core functionality for device discovery and management
"""

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
