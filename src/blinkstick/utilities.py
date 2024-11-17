def string_to_info_block_data(data: str) -> bytes:
    """
    Helper method to convert a string to byte array of 32 bytes.

    @type  data: str
    @param data: The data to convert to byte array

    @rtype: byte[32]
    @return: It fills the rest of bytes with zeros.
    """
    byte_array = bytearray([1])
    for c in data:
        byte_array.append(ord(c))

    for i in range(32 - len(data)):
        byte_array.append(0)

    return bytes(byte_array)
