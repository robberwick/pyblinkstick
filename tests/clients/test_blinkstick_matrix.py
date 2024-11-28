from blinkstick.clients.blinkstick import BlinkStickProMatrix


def test_instantiate():
    bs = BlinkStickProMatrix()
    assert bs is not None
