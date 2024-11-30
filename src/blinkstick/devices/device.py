from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class BlinkStickDevice(Generic[T]):
    """A BlinkStick device representation"""

    raw_device: T
    serial: str
    manufacturer: str
    version_attribute: int
    description: str
