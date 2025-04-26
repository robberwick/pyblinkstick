"""
Base module for BlinkStick animations.

This module provides the fundamental building blocks for creating animations
on BlinkStick devices. It includes the base Animation class that defines
the interface for all animations and the AnimationState enum for tracking
animation status.
"""

from __future__ import annotations

import threading
from abc import ABC, abstractmethod
import threading
from typing import Optional, Any
from enum import Enum, auto

from blinkstick.colors import RGBColor
from blinkstick.utilities import convert_to_rgb_color


class AnimationState(Enum):
    """
    Enumeration of possible states for an animation.

    States:
        QUEUED: Animation is waiting to be executed
        RUNNING: Animation is currently being executed
        COMPLETED: Animation has finished successfully
        CANCELLED: Animation was cancelled before completion
    """

    QUEUED = auto()
    RUNNING = auto()
    COMPLETED = auto()
    CANCELLED = auto()


class Animation(ABC):
    """
    Abstract base class for all BlinkStick animations.

    This class defines the interface that all animations must implement and provides
    common functionality for animation control and state management.

    Args:
        blinkstick: The BlinkStick device to animate
        color: Target RGB color for the animation
        channel: LED channel to use (default: Channel.RED)
        index: LED index to animate (default: 0)

    Attributes:
        blinkstick: Reference to the BlinkStick device
        target_color: The target RGB color for the animation
        channel: The LED channel being used
        index: The LED index being animated
        state: Current state of the animation
        frame_rate: Animation frame rate in frames per second (default: 30)
    """

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
        """
        An abstract method that must be implemented by subclasses to define specific
        execution behavior. This method is designed to enforce implementation in derived
        classes for executing a certain action or series of actions.

        :raises NotImplementedError: If the subclass does not implement this method.

        :return: None
        """
        pass

    def cancel(self) -> None:
        """
        Stops the animation process and updates the animation state to CANCELLED.

        This method sets an internal stop event to signal the animation process to
        halt, and it changes the current animation state to indicate cancellation.

        No value is returned from this method as it directly modifies the animation
        state and control attributes.

        :raises RuntimeError: If the method is called in an invalid state.
        """
        self._stop_event.set()
        self.state = AnimationState.CANCELLED

    @property
    def is_cancelled(self) -> bool:
        """
        Checks whether the operation has been cancelled.

        This property evaluates the state of an internal event to determine whether
        a cancellation signal has been received.

        :return: True if the operation has been cancelled, False otherwise
        :rtype: bool
        """
        return self._stop_event.is_set()

    @property
    def step_length(self) -> float:
        """
        Provides the step length in milliseconds, calculated based on the frame rate.

        :return: The step length, expressed in milliseconds.
        :rtype: float
        """
        return (1.0 / self.frame_rate) * 1000.0
