"""
The clients package provides classes for interacting with different BlinkStick device models.

This package includes client implementations for:
- BlinkStick
- BlinkStickFlex
- BlinkStickNano
- BlinkStickPro
- BlinkStickSquare
- BlinkStickStrip

Each client provides a consistent interface for controlling LED colors and animations
while handling the specific features and requirements of each device model.
"""

from .blinkstick import BlinkStick

__all__ = ["BlinkStick", "BlinkStickPro", "BlinkStickProMatrix"]
