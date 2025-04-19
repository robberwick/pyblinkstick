import time

from blinkstick.clients import BlinkStick
from blinkstick.animation.base import Animation, AnimationState
from blinkstick.colors import RGBColor
from blinkstick.enums import Channel


class MorphAnimation(Animation):
    def __init__(
        self,
        blinkstick: BlinkStick,
        color: RGBColor,
        channel: Channel = Channel.RED,
        index: int = 0,
        duration: int = 1000,
        steps: int = 50,
    ):
        super().__init__(blinkstick, color, channel, index)
        self.duration = duration
        self.steps = steps

    def run(self) -> None:
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
