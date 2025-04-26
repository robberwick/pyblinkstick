"""
This module provides color morphing animation functionality for BlinkStick devices.

It contains the MorphAnimation class which enables smooth color transitions
between different RGB values over a specified duration.
"""

from __future__ import annotations

import time

from blinkstick.clients import BlinkStick
from blinkstick.animation.base import Animation, AnimationState
from blinkstick.colors import RGBColor
from blinkstick.enums import Channel


class MorphAnimation(Animation):
    """
    Implements a smooth color transition animation for BlinkStick devices.

    This animation gradually changes the LED color from its current value
    to a target color over a specified duration, creating a smooth morphing effect.
    The transition is broken down into smaller steps for smoother appearance.
    """

    def __init__(
        self,
        blinkstick: BlinkStick,
        color: RGBColor,
        channel: Channel = Channel.RED,
        index: int = 0,
        duration: int = 1000,
        steps: int = 50,
    ):
        """
        Initialize a new color morphing animation.

        :param blinkstick: The BlinkStick device to control
        :param color: Target RGB color to morph to
        :param channel: Color channel to use (default: RED)
        :param index: LED index to animate (default: 0)
        :param duration: Total animation duration in milliseconds (default: 1000)
        :param steps: Number of intermediate steps for the transition (default: 50)
        """
        super().__init__(blinkstick, color, channel, index)
        self.duration = duration
        self.steps = steps

    def run(self) -> None:
        """
        Execute the morphing animation.

        Gradually transitions the LED color from its current value to the target color
        over the specified duration. The transition is broken into steps, with each step
        updating the color values proportionally. The animation can be cancelled mid-execution
        by setting the is_cancelled flag.
        """
        self.state = AnimationState.RUNNING
        current_color = self.blinkstick.get_color(index=self.index)

        step_time = self.duration / self.steps / 1000
        red_step = (self.target_color.red - current_color.red) / self.steps
        green_step = (self.target_color.green - current_color.green) / self.steps
        blue_step = (self.target_color.blue - current_color.blue) / self.steps

        for step in range(self.steps + 1):
            if self.is_cancelled:
                return

            red = int(current_color.red + red_step * step)
            green = int(current_color.green + green_step * step)
            blue = int(current_color.blue + blue_step * step)

            red = max(0, min(255, red))
            green = max(0, min(255, green))
            blue = max(0, min(255, blue))

            intermediate_color = RGBColor(red=red, green=green, blue=blue)
            self.blinkstick.set_color(
                intermediate_color, channel=self.channel, index=self.index
            )

            if step < self.steps:
                time.sleep(step_time)

        self.state = AnimationState.COMPLETED
