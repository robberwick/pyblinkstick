from __future__ import annotations

from abc import ABC, abstractmethod


class BaseBackend(ABC):

    serial: str | None

    def __init__(self):
        self.serial = None

    @abstractmethod
    def _refresh_device(self):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def find_blinksticks(find_all: bool = True):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def find_by_serial(serial: str) -> BaseBackend | None:
        raise NotImplementedError

    @abstractmethod
    def control_transfer(self, bmRequestType: int, bRequest: int, wValue: int, wIndex: int, data_or_wLength: bytes | int):
        raise NotImplementedError

    @abstractmethod
    def get_serial(self):
        raise NotImplementedError

    @abstractmethod
    def get_manufacturer(self):
        raise NotImplementedError

    @abstractmethod
    def get_version_attribute(self):
        raise NotImplementedError

    @abstractmethod
    def get_description(self):
        raise NotImplementedError
