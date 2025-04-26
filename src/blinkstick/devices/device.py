"""
BlinkStick device management and abstraction module.

This module provides the foundation for working with BlinkStick USB LED devices through
a flexible abstraction layer. It handles device identification, variant detection,
and property management for all supported BlinkStick hardware versions.

Classes:
    BlinkStickDevice: A generic wrapper class that encapsulates physical BlinkStick
        devices and provides a consistent interface for accessing their properties
        and capabilities.

Type Variables:
    T: Generic type parameter for raw device implementation, allowing the
       BlinkStickDevice class to work with different underlying USB handlers.

Dependencies:
    - BlinkStickVariant: Enumeration defining supported device variants and versions
    - SerialDetails: Data model for device serial number and version information

Example:
    from blinkstick.devices import BlinkStickDevice
    from blinkstick.models import SerialDetails

    # Create a device instance
    device = BlinkStickDevice(
        raw_device=usb_device,
        serial_details=SerialDetails("BS000123", 1),
        manufacturer="Agile Innovative Ltd",
        version_attribute=1,
        description="BlinkStick Square"
    )

    # Access device properties
    print(f"Device variant: {device.variant}")
    print(f"Major version: {device.major_version}")
"""

from dataclasses import dataclass, field
from typing import Generic, TypeVar

from blinkstick.enums import BlinkStickVariant
from blinkstick.models import SerialDetails

T = TypeVar("T")


@dataclass
class BlinkStickDevice(Generic[T]):
    """
    Represents a BlinkStick device with relevant details and attributes.

    This is a generic class that wraps around a raw device and provides properties
    such as serial details, manufacturer information, versioning, and device variants.
    It initializes additional details and variant information based on the
    provided serial details and version attributes.

    :ivar raw_device: The raw device object representing the physical BlinkStick device.
    :type raw_device: T
    :ivar serial_details: The serial details of the BlinkStick device including
        major version information.
    :type serial_details: SerialDetails
    :ivar manufacturer: The name of the device's manufacturer.
    :type manufacturer: str
    :ivar version_attribute: An attribute that represents version-specific details
        of the device.
    :type version_attribute: int
    :ivar description: A textual description or identifier of the BlinkStick device.
    :type description: str
    :ivar major_version: The major version of the device, inferred from
        `serial_details`. This attribute is initialized automatically during
        object construction.
    :type major_version: int
    :ivar variant: The specific variant of the BlinkStick device, determined by
        its major version and version attribute. This attribute is initialized
        automatically during object construction.
    :type variant: BlinkStickVariant
    """

    raw_device: T
    serial_details: SerialDetails
    manufacturer: str
    version_attribute: int
    description: str
    major_version: int = field(init=False)
    variant: BlinkStickVariant = field(init=False)

    def __post_init__(self):
        self.major_version = self.serial_details.major_version
        self.variant = BlinkStickVariant.from_version_attrs(
            major_version=self.serial_details.major_version,
            version_attribute=self.version_attribute,
        )
