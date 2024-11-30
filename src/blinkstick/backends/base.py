from __future__ import annotations

from abc import ABC, abstractmethod

from typing import TypeVar, Generic

from blinkstick.devices.device import BlinkStickDevice

T = TypeVar("T")


class BaseBackend(ABC, Generic[T]):

    serial: str | None
    blinkstick_device: BlinkStickDevice[T]

    def __init__(self):
        self.serial = None

    @abstractmethod
    def _refresh_attached_blinkstick_device(self):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def get_attached_blinkstick_devices(
        find_all: bool = True,
    ) -> list[BlinkStickDevice[T]]:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def find_by_serial(serial: str) -> list[BlinkStickDevice[T]] | None:
        raise NotImplementedError

    @abstractmethod
    def control_transfer(
        self,
        bmRequestType: int,
        bRequest: int,
        wValue: int,
        wIndex: int,
        data_or_wLength: bytes | int,
    ):
        raise NotImplementedError

    def get_serial(self) -> str:
        return self.blinkstick_device.serial

    def get_manufacturer(self) -> str:
        return self.blinkstick_device.manufacturer

    def get_version_attribute(self) -> int:
        return self.blinkstick_device.version_attribute

    def get_description(self):
        return self.blinkstick_device.description
