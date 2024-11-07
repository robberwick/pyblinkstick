import pytest
from pytest_mock import MockFixture

from blinkstick.blinkstick import BlinkStick, BlinkStickException

def test_get_color_rgb(mocker: MockFixture):
    """Test get_color with color_format='rgb'. We expect it to return the color in RGB format."""
    mock_get_color_rgb = mocker.patch.object(BlinkStick, '_get_color_rgb', return_value=(255, 0, 0))
    blinkstick = BlinkStick()
    assert blinkstick.get_color() == (255, 0, 0)
    assert mock_get_color_rgb.call_count == 1

def test_get_color_hex(mocker):
    """Test get_color with color_format='hex'. We expect it to return the color in hex format."""
    mock_get_color_hex = mocker.patch.object(BlinkStick, '_get_color_hex', return_value='#ff0000')
    blinkstick = BlinkStick()
    assert blinkstick.get_color(color_format='hex') == '#ff0000'
    assert mock_get_color_hex.call_count == 1

def test_get_color_invalid_format(mocker):
    """Test get_color with invalid color_format. We expect it not to raise an exception, but to default to RGB."""
    mock_get_color_rgb = mocker.patch.object(BlinkStick, '_get_color_rgb', return_value=(255, 0, 0))
    blinkstick = BlinkStick()
    blinkstick.get_color(color_format='invalid_format')
    assert mock_get_color_rgb.call_count == 1

def test_non_callable_get_color(mocker):
    """Test get_color with a non-callable get_color_func. We expect it to raise an exception."""
    blinkstick = BlinkStick()
    blinkstick._get_color_rgb = 'not_a_callable'
    with pytest.raises(BlinkStickException):
        blinkstick.get_color()