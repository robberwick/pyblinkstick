"""
The animation package provides classes and utilities for creating and managing LED animations
with BlinkStick devices.

This package includes:
- Animator: Coordinates and manages the execution of animations on a separate thread
- Animation: Base class for all animations
- BlinkAnimation: Creates simple blinking effects with configurable timing and colors

Example usage:
    from blinkstick.animation import Animator
    from blinkstick.animation.blink import BlinkAnimation
    from blinkstick.colors import RGBColor

    # Create an animator instance
    animator = Animator(blinkstick_device)

    # Create and queue a blink animation
    blink = BlinkAnimation(
        blinkstick_device,
        RGBColor(255, 0, 0),  # Red color
        repeats=3,            # Blink 3 times
        delay=500            # 500ms between states
    )
    animator.queue_animation(blink)
"""
