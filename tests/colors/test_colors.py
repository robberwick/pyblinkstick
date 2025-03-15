import pytest

from blinkstick.colors import (
    NamedColor,
    RGBColor,
)


def test_all_named_colors_present(w3c_colors):
    assert {name for name, _ in w3c_colors} == {color.name for color in NamedColor}


def test_all_named_colors_are_correct_hex_values(w3c_colors):
    assert set(w3c_colors) == {(color.name, color.value.hex) for color in NamedColor}


def test_named_color_invalid():
    with pytest.raises(
        ValueError, match="'invalidcolor' is not defined as a named color."
    ):
        NamedColor.from_name("invalidcolor")


def test_named_color_case_insensitive(w3c_colors):
    for color_name, _ in w3c_colors:
        assert (
            NamedColor.from_name(color_name.upper()) == NamedColor[color_name.upper()]
        )
        assert (
            NamedColor.from_name(color_name.lower()) == NamedColor[color_name.upper()]
        )


@pytest.mark.parametrize(
    "input_value, expected_output",
    [
        ("#ffffff", "#ffffff"),
        ("#FFFFFF", "#ffffff"),
        ("#fff", "#ffffff"),
        ("#FFF", "#ffffff"),
        ("ffffff", "#ffffff"),
        ("FFFFFF", "#ffffff"),
        ("fff", "#ffffff"),
        ("FFF", "#ffffff"),
    ],
)
def test_rgb_colour_hex_from_hex(input_value, expected_output):
    assert RGBColor.from_hex(input_value).hex == expected_output


def test_remap_rgb_to_smaller_range():
    # RGB(255, 128, 64) remapped to max 10 should be (10, 5, 3)
    color = RGBColor(255, 128, 64)
    remapped = color.remap_to_new_range(10)
    assert remapped.red == 10
    assert remapped.green == 5
    assert remapped.blue == 2


def test_remap_to_out_of_bounds():
    # RGB(255, 128, 64) remapped to max 1000 should be (255, 128, 64)
    color = RGBColor(255, 128, 64)
    remapped = color.remap_to_new_range(1000)
    assert remapped.red == 255
    assert remapped.green == 128
    assert remapped.blue == 64


def test_remap_rgb_to_same_range():
    # Remapping to 255 should return same values
    color = RGBColor(255, 128, 64)
    remapped = color.remap_to_new_range(255)
    assert remapped.red == 255
    assert remapped.green == 128
    assert remapped.blue == 64


def test_remap_zero_rgb_values():
    # Zero values should remain zero in any range
    color = RGBColor(0, 0, 0)
    remapped = color.remap_to_new_range(100)
    assert remapped.red == 0
    assert remapped.green == 0
    assert remapped.blue == 0


def test_remap_to_zero_range():
    # Remapping to 0 should result in all zeros
    color = RGBColor(255, 128, 64)
    remapped = color.remap_to_new_range(0)
    assert remapped.red == 0
    assert remapped.green == 0
    assert remapped.blue == 0


def test_remap_with_rounding():
    # RGB(10, 10, 10) to max 4 should round to (0, 0, 0)
    color = RGBColor(10, 10, 10)
    remapped = color.remap_to_new_range(4)
    assert remapped.red == 0
    assert remapped.green == 0
    assert remapped.blue == 0


def test_remap_with_negative_max_value():
    # Negative max_value should be clamped to 0
    color = RGBColor(255, 128, 64)
    remapped = color.remap_to_new_range(-10)
    assert remapped.red == 0
    assert remapped.green == 0
    assert remapped.blue == 0


def test_remap_with_boundary_values():
    # Test exact mapping of 255 to max_value
    color = RGBColor(255, 127, 63)
    remapped = color.remap_to_new_range(127)
    assert remapped.red == 127
    assert remapped.green == 63
    assert remapped.blue == 31


def test_remap_preserves_original():
    # Verify remapping creates a new instance without modifying original
    color = RGBColor(255, 128, 64)
    remapped = color.remap_to_new_range(100)
    assert color.red == 255
    assert color.green == 128
    assert color.blue == 64
    assert remapped is not color


def test_remap_fractional_results():
    # Test rounding behavior with values that don't map evenly
    color = RGBColor(15, 7, 3)
    remapped = color.remap_to_new_range(10)
    assert remapped.red == 0
    assert remapped.green == 0
    assert remapped.blue == 0
