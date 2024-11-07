from unittest.mock import MagicMock

import pytest

from blinkstick.blinkstick import BlinkStick
from tests.conftest import blinkstick


def test_instantiate():
    bs = BlinkStick()
    assert bs is not None

@pytest.mark.parametrize("serial, version_attribute, expected_variant, expected_variant_value", [
    ("BS12345-1.0", 0x0000, BlinkStick.BLINKSTICK, 1),
    ("BS12345-2.0", 0x0000, BlinkStick.BLINKSTICK_PRO, 2),
    ("BS12345-3.0", 0x200, BlinkStick.BLINKSTICK_SQUARE, 4), # major version 3, version attribute 0x200 is BlinkStickSquare
    ("BS12345-3.0", 0x201, BlinkStick.BLINKSTICK_STRIP, 3), # major version 3 is BlinkStickStrip
    ("BS12345-3.0", 0x202, BlinkStick.BLINKSTICK_NANO, 5),
    ("BS12345-3.0", 0x203, BlinkStick.BLINKSTICK_FLEX, 6),
    ("BS12345-4.0", 0x0000, BlinkStick.UNKNOWN, 0),
    ("BS12345-3.0", 0x9999, BlinkStick.UNKNOWN, 0),
    ("BS12345-0.0", 0x0000, BlinkStick.UNKNOWN, 0),
], ids=[
    "v1==BlinkStick",
    "v2==BlinkStickPro",
    "v3,0x200==BlinkStickSquare",
    "v3,0x201==BlinkStickStrip",
    "v3,0x202==BlinkStickNano",
    "v3,0x203==BlinkStickFlex",
    "v4==Unknown",
    "v3,Unknown==Unknown",
    "v0,0==Unknown"
])
def test_get_variant(blinkstick, serial, version_attribute, expected_variant, expected_variant_value):
    blinkstick.get_serial = MagicMock(return_value=serial)
    blinkstick.backend.get_version_attribute = MagicMock(return_value=version_attribute)
    assert blinkstick.get_variant() == expected_variant
    assert blinkstick.get_variant() == expected_variant_value


@pytest.mark.parametrize("variant_value, expected_variant, expected_name", [
    (1, BlinkStick.BLINKSTICK, "BlinkStick"),
    (2, BlinkStick.BLINKSTICK_PRO, "BlinkStick Pro"),
    (3, BlinkStick.BLINKSTICK_STRIP, "BlinkStick Strip"),
    (4, BlinkStick.BLINKSTICK_SQUARE, "BlinkStick Square"),
    (5, BlinkStick.BLINKSTICK_NANO, "BlinkStick Nano"),
    (6, BlinkStick.BLINKSTICK_FLEX, "BlinkStick Flex"),
    (0, BlinkStick.UNKNOWN, "Unknown"),
], ids=[
    "1==BlinkStick",
    "2==BlinkStickPro",
    "3==BlinkStickStrip",
    "4==BlinkStickSquare",
    "5==BlinkStickNano",
    "6==BlinkStickFlex",
    "0==Unknown"
])
def test_get_variant_string(blinkstick, variant_value, expected_variant, expected_name):
    """Test get_variant method for version 0 returns BlinkStick.UNKNOWN (0)"""
    blinkstick.get_variant = MagicMock(return_value=variant_value)
    assert blinkstick.get_variant_string() == expected_name
