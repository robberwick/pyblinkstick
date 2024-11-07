from unittest.mock import MagicMock

import pytest

from blinkstick.blinkstick import BlinkStick


@pytest.fixture
def blinkstick():
    bs = BlinkStick()
    bs.backend = MagicMock()
    return bs
