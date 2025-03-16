import queue
import threading
import time
from queue import Queue
from typing import Optional, List, Type

from typing import Optional, List, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from blinkstick.clients import BlinkStick
from blinkstick.animation.base import Animation


class Animator:
    def __init__(self, blinkstick: "BlinkStick"):
        self.blinkstick = blinkstick
        self.animation_queue: Queue[Animation] = queue.Queue()
        self.current_animation: Optional[Animation] = None
        self._animation_thread: Optional[threading.Thread] = None
        self._running = False
        self._lock = threading.RLock()

    def start(self) -> None:
        """Start the animation thread"""
        with self._lock:
            if self._running:
                return

            self._running = True
            self._animation_thread = threading.Thread(
                target=self._animation_worker, daemon=True
            )
            self._animation_thread.start()

    def stop(self) -> None:
        """Stop the animation thread and clear the queue"""
        with self._lock:
            if not self._running:
                return

            self._running = False
            if self.current_animation:
                self.current_animation.cancel()

            # Clear the queue
            while not self.animation_queue.empty():
                try:
                    animation = self.animation_queue.get_nowait()
                    animation.cancel()
                    self.animation_queue.task_done()
                except queue.Empty:
                    break

    def _animation_worker(self) -> None:
        """Main animation processing loop"""
        while self._running:
            try:
                animation = self.animation_queue.get(timeout=0.1)
                with self._lock:
                    self.current_animation = animation

                animation.run()

                with self._lock:
                    self.current_animation = None

                self.animation_queue.task_done()
            except queue.Empty:
                time.sleep(0.01)  # Avoid busy waiting
            except Exception as e:
                print(f"Animation error: {e}")

    def queue_animation(self, animation: Animation) -> None:
        """Add animation to the queue"""
        if not self._running:
            self.start()
        self.animation_queue.put(animation)

    def animate_immediately(self, animation: Animation) -> None:
        """Cancel current animation and start the new one immediately"""
        with self._lock:
            # Cancel current animation if running
            if self.current_animation:
                self.current_animation.cancel()

            # Clear the queue
            while not self.animation_queue.empty():
                try:
                    queued_animation = self.animation_queue.get_nowait()
                    queued_animation.cancel()
                    self.animation_queue.task_done()
                except queue.Empty:
                    break

            # Queue the new animation
            self.animation_queue.put(animation)

    @property
    def is_animating(self) -> bool:
        """Check if any animations are running or queued"""
        return self.current_animation is not None or not self.animation_queue.empty()
