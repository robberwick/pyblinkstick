import time
from unittest.mock import MagicMock, patch

import pytest

from blinkstick import BlinkStick
from src.blinkstick.animation.animator import Animator
from src.blinkstick.animation.base import Animation


@pytest.fixture
def mock_blinkstick():
    """
    Mock fixture for BlinkStick device. This fixture generates a mocked instance
    of BlinkStick using the MagicMock utility. It can be utilized in unit tests
    to simulate the behavior of a BlinkStick device without requiring physical
    hardware access. The mock allows for controlled interaction and behavior
    inspection.

    :return: A MagicMock instance representing a fake BlinkStick device.
    :rtype: MagicMock
    """
    return MagicMock()


@pytest.fixture
def animator(mock_blinkstick: BlinkStick) -> Animator:
    """
    Fixture for initializing an Animator instance with a mocked BlinkStick device.

    This fixture provides an Animator object that uses the mock_blinkstick
    provided as its BlinkStick device parameter. It is intended for use in
    unit tests where the actual hardware interaction by BlinkStick is not
    required, allowing tests to simulate behaviors and functionality in
    a controlled environment.

    :param mock_blinkstick: The mocked BlinkStick device to be used by the
        Animator instance.
    :type mock_blinkstick: BlinkStick
    :return: An instance of Animator configured with the mocked BlinkStick
        device.
    :rtype: Animator
    """
    return Animator(mock_blinkstick)


@pytest.fixture
def mock_animation():
    """
    Mock fixture for creating a MagicMock object simulating an Animation instance.

    This fixture provides a mocked instance of the `Animation` class, enabling unit tests
    to use this mock object in situations where the behavior of `Animation` needs to be
    simulated without using an actual implementation of the class.

    :return: A MagicMock instance simulating an Animation object.
    :rtype: MagicMock
    """
    animation = MagicMock(spec=Animation)
    return animation


def test_animator_starts_thread(animator):
    """
    Test whether the animator starts its animation thread correctly.

    The function verifies if the `animator` instance correctly transitions its
    state to `_running`, initializes its `_animation_thread`, and ensures
    the thread is active after calling the `start` method.

    :param animator: The animator instance to be tested.
    :type animator: Animator
    :return: None
    """
    assert not animator._running
    animator.start()
    assert animator._running
    assert animator._animation_thread is not None
    assert animator._animation_thread.is_alive()


def test_animator_stops_thread(animator, mock_animation):
    """
    Tests that the animator properly stops its thread, resets current
    animation, and clears the animation queue.

    This function verifies the behavior of the animator when stopped
    during its operation. It ensures that the animator ceases execution,
    releases any ongoing animation, and clears all queued animations.

    :param animator: The animator instance to be tested.
    :param mock_animation: A mock object representing the animation
        to be queued in the animator.
    :return: None
    """
    animator.start()
    animator.queue_animation(mock_animation)
    animator.stop()

    assert not animator._running
    assert animator.current_animation is None
    assert animator.animation_queue.empty()


def test_queue_animation_starts_animator(animator, mock_animation):
    """
    Tests that queuing an animation using the animator starts the corresponding
    animation process. Initially, the `animator` instance is checked to confirm
    it is not running. Upon queuing the `mock_animation`, it asserts that the
    animator begins running, and the animation queue is no longer empty.

    :param animator: The animator object to be tested.
    :type animator: Animator
    :param mock_animation: The mock animation instance to be queued.
    :type mock_animation: Animation
    :return: None
    """
    assert not animator._running
    animator.queue_animation(mock_animation)
    assert animator._running
    assert not animator.animation_queue.empty()


def test_animate_immediately_cancels_current_and_requeues(animator, mock_animation):
    """
    Tests that the `animate_immediately` method cancels any currently running
    animation, clears the animation queue, and requeues the provided animation.

    :param animator: Animator instance responsible for handling animations.
    :type animator: Animator
    :param mock_animation: The current animation being handled and subjected to
        cancellation during the test.
    :type mock_animation: Animation
    :return: None
    """
    another_mock_animation = MagicMock(spec=Animation)

    animator.start()
    animator.queue_animation(mock_animation)
    animator.animate_immediately(another_mock_animation)

    assert animator.current_animation is None
    assert not animator.animation_queue.empty()
    assert animator.animation_queue.get() == another_mock_animation
    mock_animation.cancel.assert_called_once()


def test_is_animating_returns_correct_state(animator, mock_animation):
    """
    Tests if the `is_animating` method returns the correct animation state.

    The function evaluates whether the `is_animating` attribute of the
    animator correctly reflects the presence of enqueued animations. It
    initially verifies that the animator is not animating, then queues an
    animation and checks that the state updates appropriately.

    :param animator: An instance of the animator being tested.
    :param mock_animation: A mock animation object to be queued in the
        animator.
    :return: None
    """
    assert not animator.is_animating
    animator.queue_animation(mock_animation)
    assert animator.is_animating


@pytest.mark.parametrize("initially_running", [True, False])
def test_start_behavior_based_on_initial_state(animator, initially_running):
    """
    Test the Animator's `start` method behavior based on its initial state.
    - If stopped (initially_running=False), it should start and create a new thread.
    - If already running (initially_running=True), it should remain running
      and not replace the existing thread.

    :param animator: The Animator object being tested.
    :param initially_running: Boolean indicating the desired initial state for the test.
    :return: None
    """
    initial_thread = None

    try:
        # --- Setup phase: Establish the initial state ---
        if initially_running:
            # Start the animator properly to create the thread and set flags
            animator.start()
            # Wait briefly for the thread to actually start
            time.sleep(0.05)
            assert animator._running is True, "Animator should be running after initial start"
            assert animator._animation_thread is not None, "Thread should exist after initial start"
            assert animator._animation_thread.is_alive(), "Thread should be alive after initial start"
            initial_thread = animator._animation_thread
        else:
            # Ensure the animator starts in a non-running state
            assert animator._running is False, "Animator should initially be stopped"
            assert animator._animation_thread is None, "Animator thread should initially be None"

        # --- Action phase: Call start() again (the actual operation under test) ---
        animator.start()
        # Give it a moment if it needed to start a thread
        if not initially_running:
            time.sleep(0.05)

        # --- Assertion phase ---
        assert animator._running is True, "Animator should be running after the tested start() call"
        current_thread = animator._animation_thread
        assert current_thread is not None, "Animator thread should exist after the tested start() call"
        assert current_thread.is_alive(), "Animator thread should be alive after the tested start() call"

        if initially_running:
            # If it was already running, the thread instance should NOT have changed.
            assert current_thread is initial_thread, "Thread instance should not change if already running"
        # No specific 'else' assertion needed here for the thread instance,
        # as we just need to ensure *a* thread exists and is alive.

    finally:
        # --- Cleanup phase ---
        if animator._running:
            animator.stop()
            # Wait for the thread to terminate if stop() isn't fully blocking
            thread_to_join = initial_thread if initially_running else animator._animation_thread
            if thread_to_join and thread_to_join.is_alive():
                # Use the captured thread object for joining
                thread_to_join.join(timeout=1.0)
            # Check animator state after stop
            assert animator._running is False, "Animator should be stopped after cleanup"
