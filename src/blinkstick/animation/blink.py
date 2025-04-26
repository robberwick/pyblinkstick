"""
This module provides the BlinkAnimation class for creating simple blinking effects
with BlinkStick devices. It enables control over blink timing, color, and repetition.
"""

from __future__ import annotations

import time

from blinkstick.clients import BlinkStick
from blinkstick.animation.base import Animation, AnimationState
from blinkstick.colors import RGBColor
from blinkstick.enums import Channel


class BlinkAnimation(Animation):
    """
    Creates a blinking animation effect for a BlinkStick device.

    The animation alternates between the specified color and off state with
    a configurable delay between state changes.

    :param blinkstick: The BlinkStick device to control.
    :param color: The RGB color to display during the 'on' state.
    :param channel: The LED channel to control (default: Channel.RED).
    :param index: The LED index to control (default: 0).
    :param repeats: Number of times to repeat the blink sequence (default: 1).
    :param delay: Delay in milliseconds between state changes (default: 500).
    """

    def __init__(
        self,
        blinkstick: BlinkStick,
        color: RGBColor,
        channel: Channel = Channel.RED,
        index: int = 0,
        repeats: int = 1,
        delay: int = 500,
    ):
        super().__init__(blinkstick, color, channel, index)
        self.repeats = repeats
        self.delay_sec = delay / 1000.0

    def run(self) -> None:
        """
        Executes the blink animation sequence.

        The method alternates between the target color and off state for the specified
        number of repeats. Each state change is separated by the configured delay.
        The animation can be cancelled at any time by setting is_cancelled to True.
        """
        self.state = AnimationState.RUNNING

        for i in range(self.repeats):
            if self.is_cancelled:
                return

            if i > 0:
                time.sleep(self.delay_sec)
                if self.is_cancelled:
                    return

            self.blinkstick.set_color(
                self.target_color, channel=self.channel, index=self.index
            )
            time.sleep(self.delay_sec)
            if self.is_cancelled:
                return

            self.blinkstick.turn_off()

        self.state = AnimationState.COMPLETED
