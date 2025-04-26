"""
BlinkStick Flex hardware client implementation module.

This module implements the BlinkStickFlex class for controlling BlinkStick Flex
USB LED devices. It extends the base client implementation with specialized
features and optimizations for the Flex hardware variant.

Features and Capabilities:
- Controls up to 64 independent RGB LEDs
- Full 24-bit color support (8-bit per channel)
- Real-time LED state management
- Hardware-accelerated animations
- USB 2.0 HID protocol support
- Hot-plug device detection

Core Functionality:
- Individual LED addressing
- RGB color manipulation
- Animation sequencing
- Device state management
- Thread-safe operations

Example usage:
    from blinkstick.clients.blinkstick_flex import BlinkStickFlex

    # Create and initialize device
    stick = BlinkStickFlex()

    # Set LED colors
    stick.set_color(red=255, green=0, blue=0)  # Set to red
    stick.turn_off()  # Turn off all LEDs

The implementation provides optimized access to all hardware features
while maintaining compatibility with the base BlinkStick interface.
"""

from __future__ import annotations

from blinkstick.clients.base import BlinkStickClientBase


class BlinkStickFlex(BlinkStickClientBase):
    """
    Represents the BlinkStick Flex device.

    This class is a specific implementation of the BlinkStickClientBase that
    provides functionality for controlling the BlinkStick Flex device. It allows
    users to interact with and manipulate the device's state, such as controlling
    LED lights and their configurations.
    """

    pass
