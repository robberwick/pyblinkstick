from dataclasses import dataclass, field
from typing import Generic, TypeVar

from blinkstick.enums import BlinkStickVariant

T = TypeVar("T")


@dataclass
class BlinkStickDevice(Generic[T]):
    """A BlinkStick device representation"""

    raw_device: T
    serial: str
    manufacturer: str
    version_attribute: int
    description: str
    major_version: int = field(init=False)
    variant: BlinkStickVariant = field(init=False)

    def __post_init__(self):
        self.major_version = int(self.serial[-3])
        self.variant = BlinkStickVariant.from_version_attrs(
            major_version=self.major_version, version_attribute=self.version_attribute
        )
