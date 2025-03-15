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
