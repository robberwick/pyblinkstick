import time

from blinkstick.clients import BlinkStick
from blinkstick.animation.base import Animation, AnimationState
from blinkstick.colors import RGBColor
from blinkstick.enums import Channel


class BlinkAnimation(Animation):
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
