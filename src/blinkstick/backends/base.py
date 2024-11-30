from __future__ import annotations

from abc import ABC, abstractmethod

from typing import TypeVar, Generic

T = TypeVar("T")


class BaseBackend(ABC, Generic[T]):

    serial: str | None

    def __init__(self):
        self.serial = None

    @abstractmethod
    def _refresh_attached_blinkstick_device(self):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def get_attached_blinkstick_devices(find_all: bool = True) -> list[T]:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def find_by_serial(serial: str) -> list[T] | None:
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

    @abstractmethod
    def get_serial(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_manufacturer(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_version_attribute(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def get_description(self) -> str:
        raise NotImplementedError
