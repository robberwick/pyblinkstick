"""
This module provides the PulseAnimation class for creating pulsing light effects with BlinkStick devices.

The module implements functionality for smoothly transitioning an LED between a target color and black,
creating a pulsing or heartbeat-like effect.
"""

from blinkstick.clients import BlinkStick
from blinkstick.animation.base import Animation, AnimationState
from blinkstick.animation.morph import MorphAnimation
from blinkstick.colors import RGBColor
from blinkstick.enums import Channel


class PulseAnimation(Animation):
    """
    Creates a pulsing effect by alternating an LED between a target color and black.

    The PulseAnimation class provides functionality to create a smooth pulsing or heartbeat-like effect
    using a BlinkStick device. It achieves this by utilizing MorphAnimation to create gradual transitions
    between the target color and black (off state).

    The animation consists of repeated cycles where each cycle includes:
    1. A transition from black to the target color
    2. A transition from the target color back to black

    The smoothness and timing of these transitions can be controlled through the steps and duration
    parameters, while the number of pulses is determined by the repeats parameter.

    :ivar repeats: Number of times the pulse animation should repeat
    :type repeats: int
    :ivar duration: Time in milliseconds for each transition (to color or to black)
    :type duration: int
    :ivar steps: Number of incremental steps in each transition
    :type steps: int
    """

    def __init__(
        self,
        blinkstick: BlinkStick,
        color: RGBColor,
        channel: Channel = Channel.RED,
        index: int = 0,
        repeats: int = 1,
        duration: int = 1000,
        steps: int = 50,
    ):
        """
        Initialize a new PulseAnimation instance.

        :param blinkstick: The BlinkStick device to control
        :param color: Target RGB color for the pulse effect
        :param channel: Color channel to use (default: RED)
        :param index: LED index to animate (default: 0)
        :param repeats: Number of pulse cycles to perform (default: 1)
        :param duration: Duration in milliseconds for each transition (default: 1000)
        :param steps: Number of steps in each transition (default: 50)
        """
        super().__init__(blinkstick, color, channel, index)
        self.repeats = repeats
        self.duration = duration
        self.steps = steps

    def run(self) -> None:
        """
        Execute the pulse animation sequence.

        This method runs the complete pulse animation, which consists of multiple cycles
        of transitions between black and the target color. Each cycle uses two MorphAnimations:
        one to transition to the target color and another to transition back to black.

        The animation can be cancelled at any point by setting is_cancelled to True.
        When completed normally, the animation state is set to COMPLETED.
        """
        self.state = AnimationState.RUNNING
        self.blinkstick.turn_off()

        for x in range(self.repeats):
            if self.is_cancelled:
                return

            # Morph to target color
            morph_to = MorphAnimation(
                self.blinkstick,
                self.target_color,
                self.channel,
                self.index,
                self.duration,
                self.steps,
            )
            morph_to.run()
            if self.is_cancelled or morph_to.is_cancelled:
                return

            # Morph back to black
            morph_back = MorphAnimation(
                self.blinkstick,
                RGBColor(red=0, green=0, blue=0),
                self.channel,
                self.index,
                self.duration,
                self.steps,
            )
            morph_back.run()
            if self.is_cancelled or morph_back.is_cancelled:
                return

        self.state = AnimationState.COMPLETED
