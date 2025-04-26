"""
Utility functions for BlinkStick operations including data conversion, color handling,
and device configuration helpers.

This module provides various helper functions used throughout the BlinkStick library
for converting between different data formats and managing device-specific configurations.
"""

from __future__ import annotations
from blinkstick.colors import RGBColor, NamedColor


def string_to_info_block_data(data: str) -> bytes:
    """
    Convert a string to a byte array of 32 bytes for info block data.

    The function prepends a 0x01 byte prefix and converts the input string to UTF-8 bytes.
    If the resulting byte array is shorter than 31 bytes (excluding prefix), it is padded
    with null bytes.

    Args:
        data: The string data to convert to a byte array.

    Returns:
        A 32-byte array containing the converted string data with padding.
    """
    max_buffer_size = 31  # 31 bytes for the string + 1 byte for the prefix
    return bytearray([0x01]) + data.encode("utf-8")[:max_buffer_size].ljust(
        max_buffer_size, b"\x00"
    )


def convert_to_rgb_color(color: RGBColor | NamedColor | str) -> RGBColor:
    """
    Convert various color representations to an RGBColor instance.

    Supports multiple input formats:
    - RGBColor instance (returned as-is)
    - NamedColor instance (converted to its RGB value)
    - String: can be a color name, 'random', or a hex color code

    Args:
        color: The color to convert, can be RGBColor, NamedColor, or string.

    Returns:
        RGBColor instance representing the input color.
        Returns black (0, 0, 0) if conversion fails.
    """
    if isinstance(color, RGBColor):
        return color
    if isinstance(color, NamedColor):
        return color.value
    if isinstance(color, str):
        if color.lower() == "random":
            return RGBColor.random()
        try:
            return NamedColor.from_name(name=color).value
        except ValueError:
            return RGBColor.from_hex(str(color))
    return RGBColor(0, 0, 0)  # Default


def determine_report_id(led_count: int) -> tuple[int, int]:
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
