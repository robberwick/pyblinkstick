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
    """
    Coordinates and manages the execution of animations using a BlinkStick device.

    This class handles the queuing and sequential execution of animations
    on a separate thread to avoid blocking the main program flow. It provides
    methods to start, stop, queue, and immediately run animations.

    :ivar blinkstick: Reference to the BlinkStick device used to execute animations.
    :ivar animation_queue: A thread-safe queue holding pending animations.
    :ivar current_animation: The animation currently being executed, if any.
    :type current_animation: Optional[Animation]
    :ivar _animation_thread: The background thread executing animations from the queue.
    :type _animation_thread: Optional[threading.Thread]
    :ivar _running: A flag indicating if the animation worker thread is active.
    :type _running: bool
    :ivar _lock: A reentrant lock ensuring thread-safe access to shared resources.
    :type _lock: threading.RLock
    """
    def __init__(self, blinkstick: "BlinkStick"):
        """
        Initializes the Animator with a BlinkStick device instance.

        :param blinkstick: The BlinkStick device instance to control.
        """
        self.blinkstick = blinkstick
        self.animation_queue: Queue[Animation] = queue.Queue()
        self.current_animation: Optional[Animation] = None
        self._animation_thread: Optional[threading.Thread] = None
        self._running = False
        self._lock = threading.RLock()

    def start(self) -> None:
        """
        Starts the background animation worker thread if it's not already running.

        Initializes and starts a daemon thread that processes the animation queue.
        This method is thread-safe.
        """
        with self._lock:
            if self._running:
                return

            self._running = True
            self._animation_thread = threading.Thread(
                target=self._animation_worker, daemon=True
            )
            self._animation_thread.start()

    def stop(self) -> None:
        """
        Stops the animation worker thread and clears the animation queue.

        Sets the running flag to False, attempts to cancel the currently
        executing animation (if any), and removes all pending animations
        from the queue. This method is thread-safe.
        """
        with self._lock:
            if not self._running:
                return

            self._running = False
            # Signal the current animation to stop, if one exists
            if self.current_animation:
                self.current_animation.cancel()

            # Clear the queue, cancelling any pending animations
            while not self.animation_queue.empty():
                try:
                    animation = self.animation_queue.get_nowait()
                    animation.cancel()  # Signal the animation to stop if needed
                    self.animation_queue.task_done()
                except queue.Empty:
                    # Should not happen in this loop logic, but handle defensively
                    break
            # Note: The thread will exit gracefully on its next loop iteration
            # or timeout check because self._running is False.

    def _animation_worker(self) -> None:
        """
        The target method for the background animation thread.

        Continuously fetches animations from the queue and executes them sequentially.
        Handles graceful shutdown when the `_running` flag is set to False.
        Includes a short timeout on the queue get to allow periodic checks
        of the `_running` flag and prevent busy-waiting.
        """
        while self._running:
            try:
                # Wait for an animation with a timeout
                animation = self.animation_queue.get(timeout=0.1)
                with self._lock:
                    # Check if stop() was called while waiting
                    if not self._running:
                        animation.cancel() # Ensure cancelled if stopped during wait
                        self.animation_queue.task_done()
                        break
                    self.current_animation = animation

                # Run the animation outside the lock to allow other operations
                # like stop() or queue_animation() concurrently.
                if self.current_animation: # Check if it was cancelled by stop()
                    try:
                        self.current_animation.run()
                    except Exception as e:
                        # Log or handle animation execution errors appropriately
                        print(f"Error during animation execution: {e}")
                    finally:
                        # Clear current_animation *after* execution or error
                        with self._lock:
                           self.current_animation = None

                self.animation_queue.task_done()

            except queue.Empty:
                # Timeout occurred, loop again to check self._running
                continue
            except Exception as e:
                # Catch potential errors in the worker loop itself
                print(f"Error in animation worker: {e}")
                # Consider whether to break the loop or continue
                time.sleep(0.1) # Prevent fast spinning on repeated errors

    def queue_animation(self, animation: Animation) -> None:
        """
        Adds an animation to the end of the execution queue.

        If the animator thread is not running, it will be started.

        :param animation: The Animation instance to add to the queue.
        """
        # Start the worker if it's not already running
        if not self._running:
            self.start()
        # Add the animation to the queue (Queue.put is thread-safe)
        self.animation_queue.put(animation)

    def animate_immediately(self, animation: Animation) -> None:
        """
        Clears the queue, cancels the current animation, and runs the new one.

        Stops and cancels the currently executing animation (if any), clears
        all pending animations from the queue, and then queues the provided
        animation to be run next. This method is thread-safe.

        :param animation: The Animation instance to run immediately.
        """
        with self._lock:
            # Cancel the current animation first
            if self.current_animation:
                self.current_animation.cancel()
                # Note: _animation_worker handles setting self.current_animation to None

            # Clear the existing queue, cancelling pending items
            while not self.animation_queue.empty():
                try:
                    queued_animation = self.animation_queue.get_nowait()
                    queued_animation.cancel()
                    self.animation_queue.task_done()
                except queue.Empty:
                    break

            # Ensure the worker is running before queueing
            if not self._running:
                self.start()

            # Queue the new animation
            self.animation_queue.put(animation)

    @property
    def is_animating(self) -> bool:
        """
        Checks if the animator is currently executing or has pending animations.

        :return: True if an animation is running or queued, False otherwise.
        :rtype: bool
        """
        # Accessing current_animation and queue emptiness needs care
        # if accessed from multiple threads, but reads are generally safe.
        # For stronger consistency, a lock could be used, but might be overkill.
        with self._lock:
            is_running = self.current_animation is not None
        is_queued = not self.animation_queue.empty()
        return is_running or is_queued