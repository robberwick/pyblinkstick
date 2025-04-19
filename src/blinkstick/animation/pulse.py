from blinkstick.clients import BlinkStick
from blinkstick.animation.base import Animation, AnimationState
from blinkstick.animation.morph import MorphAnimation
from blinkstick.colors import RGBColor
from blinkstick.enums import Channel


class PulseAnimation(Animation):
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
        super().__init__(blinkstick, color, channel, index)
        self.repeats = repeats
        self.duration = duration
        self.steps = steps

    def run(self) -> None:
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
