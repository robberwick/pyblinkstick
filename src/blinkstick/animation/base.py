from abc import ABC, abstractmethod
import threading
from typing import Optional, Any
from enum import Enum, auto

from blinkstick.colors import RGBColor
from blinkstick.utilities import convert_to_rgb_color


class AnimationState(Enum):
    QUEUED = auto()
    RUNNING = auto()
    COMPLETED = auto()
    CANCELLED = auto()


class Animation(ABC):
    def __init__(self, blinkstick, color, channel=0, index=0):
        self.blinkstick = blinkstick
        self.target_color = convert_to_rgb_color(color)
        self.channel = channel
        self.index = index
        self.state = AnimationState.QUEUED
        self._stop_event = threading.Event()
        self.frame_rate = 30  # Default frame rate

    @abstractmethod
    def run(self) -> None:
        """Run the animation until completion or cancelled"""
        pass

    def cancel(self) -> None:
        """Request cancellation of the animation"""
        self._stop_event.set()
        self.state = AnimationState.CANCELLED

    @property
    def is_cancelled(self) -> bool:
        return self._stop_event.is_set()

    @property
    def step_length(self) -> float:
        """Calculate the length of each step in seconds based on the frame rate"""
        return (1.0 / self.frame_rate) * 1000.0
