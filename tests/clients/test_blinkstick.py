from unittest.mock import MagicMock

import pytest
from blinkstick import BlinkStick

from blinkstick.blinkstick import BlinkStick
from blinkstick.constants import BlinkStickVariant
from pytest_mock import MockFixture

from tests.conftest import blinkstick


def test_instantiate():
    bs = BlinkStick()
    assert bs is not None

@pytest.mark.parametrize("serial, version_attribute, expected_variant, expected_variant_value", [
    ("BS12345-1.0", 0x0000, BlinkStickVariant.BLINKSTICK, 1),
    ("BS12345-2.0", 0x0000, BlinkStickVariant.BLINKSTICK_PRO, 2),
    ("BS12345-3.0", 0x200, BlinkStickVariant.BLINKSTICK_SQUARE, 4), # major version 3, version attribute 0x200 is BlinkStickSquare
    ("BS12345-3.0", 0x201, BlinkStickVariant.BLINKSTICK_STRIP, 3), # major version 3 is BlinkStickStrip
    ("BS12345-3.0", 0x202, BlinkStickVariant.BLINKSTICK_NANO, 5),
    ("BS12345-3.0", 0x203, BlinkStickVariant.BLINKSTICK_FLEX, 6),
    ("BS12345-4.0", 0x0000, BlinkStickVariant.UNKNOWN, 0),
    ("BS12345-3.0", 0x9999, BlinkStickVariant.UNKNOWN, 0),
    ("BS12345-0.0", 0x0000, BlinkStickVariant.UNKNOWN, 0),
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
    assert blinkstick.get_variant().value == expected_variant_value


@pytest.mark.parametrize("expected_variant, expected_name", [
    (BlinkStickVariant.BLINKSTICK, "BlinkStick"),
    (BlinkStickVariant.BLINKSTICK_PRO, "BlinkStick Pro"),
    (BlinkStickVariant.BLINKSTICK_STRIP, "BlinkStick Strip"),
    (BlinkStickVariant.BLINKSTICK_SQUARE, "BlinkStick Square"),
    (BlinkStickVariant.BLINKSTICK_NANO, "BlinkStick Nano"),
    (BlinkStickVariant.BLINKSTICK_FLEX, "BlinkStick Flex"),
    (BlinkStickVariant.UNKNOWN, "Unknown"),
], ids=[
    "1==BlinkStick",
    "2==BlinkStickPro",
    "3==BlinkStickStrip",
    "4==BlinkStickSquare",
    "5==BlinkStickNano",
    "6==BlinkStickFlex",
    "0==Unknown"
])
def test_get_variant_string(blinkstick, expected_variant, expected_name):
    """Test get_variant method for version 0 returns BlinkStick.UNKNOWN (0)"""
    blinkstick.get_variant = MagicMock(return_value=expected_variant)
    assert blinkstick.get_variant_string() == expected_name


def test_get_color_rgb_color_format(mocker: MockFixture, blinkstick: BlinkStick):
    """Test get_color with color_format='rgb'. We expect it to return the color in RGB format."""
    mock_get_color_rgb = mocker.Mock(return_value=(255, 0, 0))
    blinkstick._get_color_rgb = mock_get_color_rgb
    assert blinkstick.get_color() == (255, 0, 0)
    assert mock_get_color_rgb.call_count == 1


def test_get_color_hex_color_format(mocker: MockFixture, blinkstick: BlinkStick):
    """Test get_color with color_format='hex'. We expect it to return the color in hex format."""
    mock_get_color_hex = mocker.Mock(return_value='#ff0000')
    blinkstick._get_color_hex = mock_get_color_hex
    assert blinkstick.get_color(color_format='hex') == '#ff0000'
    assert mock_get_color_hex.call_count == 1


def test_get_color_invalid_color_format(mocker: MockFixture, blinkstick: BlinkStick):
    """Test get_color with invalid color_format. We expect it not to raise an exception, but to default to RGB."""
    mock_get_color_rgb = mocker.Mock(return_value=(255, 0, 0))
    blinkstick._get_color_rgb = mock_get_color_rgb
    blinkstick.get_color(color_format='invalid_format')
    assert mock_get_color_rgb.call_count == 1
