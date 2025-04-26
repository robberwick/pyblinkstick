"""
BlinkStick client utilities module providing device-specific client creation and type definitions.

This module implements the factory pattern for creating appropriate BlinkStick client instances
based on device variants. It provides type-safe client creation and management through:

Components:
- BlinkStickClient: Type alias for all supported client implementations
- client_factory: Factory function for creating device-specific clients
- Type checking support for static type verification

The factory pattern ensures that each device variant gets the correct client implementation:
- BlinkStick (default/standard variant)
- BlinkStickPro
- BlinkStickNano
- BlinkStickSquare
- BlinkStickStrip
- BlinkStickFlex

Example usage:
    from blinkstick.clients.utils import client_factory
    from blinkstick.devices import BlinkStickDevice

    # Create a device instance
    device = BlinkStickDevice()

    # Get the appropriate client implementation
    client = client_factory(device)

    # Use the client with type safety
    client.set_color(red=255, green=0, blue=0)

Type checking usage:
    from blinkstick.clients.utils import BlinkStickClient

    def process_device(client: BlinkStickClient) -> None:
        client.turn_off()  # Type-safe operation
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from blinkstick.devices import BlinkStickDevice

    from blinkstick.clients import (
        BlinkStick,
        BlinkStickFlex,
        BlinkStickNano,
        BlinkStickPro,
        BlinkStickStrip,
        BlinkStickSquare,
    )

    # Define the Type Alias using Union
    BlinkStickClient = Union[
        BlinkStick,
        BlinkStickFlex,
        BlinkStickPro,
        BlinkStickNano,
        BlinkStickSquare,
        BlinkStickStrip,
    ]


def client_factory(device: BlinkStickDevice) -> BlinkStickClient:
    """
    Creates an instance of the appropriate BlinkStick client based on the variant of the given
    BlinkStickDevice. Each BlinkStick variant has a specific client implementation, and this
    function determines which one to instantiate and return.

    :param device: The BlinkStickDevice object representing the device for which a client is
                   being initialized. The device's variant determines the type of client created.
    :type device: BlinkStickDevice

    :return: A client instance specific to the variant of the provided BlinkStickDevice.
    :rtype: BlinkStickClient
    """

    from blinkstick import BlinkStickVariant

    match device.variant:
        case BlinkStickVariant.BLINKSTICK_PRO:
            from blinkstick.clients.blinkstick_pro import BlinkStickPro

            return BlinkStickPro(device=device)
        case BlinkStickVariant.BLINKSTICK_NANO:
            from blinkstick.clients.blinkstick_nano import BlinkStickNano

            return BlinkStickNano(device=device)
        case BlinkStickVariant.BLINKSTICK_SQUARE:
            from blinkstick.clients.blinkstick_square import BlinkStickSquare

            return BlinkStickSquare(device=device)
        case BlinkStickVariant.BLINKSTICK_STRIP:
            from blinkstick.clients.blinkstick_strip import BlinkStickStrip

            return BlinkStickStrip(device=device)
        case BlinkStickVariant.BLINKSTICK_FLEX:
            from blinkstick.clients.blinkstick_flex import BlinkStickFlex

            return BlinkStickFlex(device=device)
        case _:
            from blinkstick.clients.blinkstick import BlinkStick

            return BlinkStick(device=device)
