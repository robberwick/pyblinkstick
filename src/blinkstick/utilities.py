from blinkstick.colors import RGBColor, NamedColor


def string_to_info_block_data(data: str) -> bytes:
    """
    Helper method to convert a string to byte array of 32 bytes.

    @type  data: str
    @param data: The data to convert to byte array

    @rtype: byte[32]
    @return: It fills the rest of bytes with zeros.
    """
    max_buffer_size = 31  # 31 bytes for the string + 1 byte for the prefix
    return bytearray([0x01]) + data.encode("utf-8")[:max_buffer_size].ljust(
        max_buffer_size, b"\x00"
    )


def convert_to_rgb_color(color: RGBColor | NamedColor | str) -> RGBColor:
    """
    Convert a value representing a colour to RGBColor. e.g. RGBColor, NamedColor, colour name or hex string.
    :param color:
    :return: RGBColor
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
