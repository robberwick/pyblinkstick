"""
The backends package implements low-level USB communication interfaces for BlinkStick devices.

Core Features:
- Device Discovery:
  - Automatic device detection
  - Serial number validation
  - Hot-plug support
  - Multi-device management

- Hardware Interface:
  - USB protocol implementation
  - Control transfer handling
  - Feature report processing
  - Error handling and recovery

- Device Control:
  - LED color manipulation
  - Operating mode configuration
  - LED strip (WS2812) support
  - Device info retrieval

Example usage:
    from blinkstick.backends import Backend

    # Initialize backend
    backend = Backend()

    # List all devices
    devices = backend.find_all()
    for device in devices:
        print(f"Found device: {device.serial}")

    # Connect to specific device
    device = backend.find_by_serial("BS012345-678")
    if device:
        # Set color
        device.set_color(red=255, green=0, blue=0)

        # Configure LED strip mode
        device.set_mode('ws2812')
        device.set_led_count(8)

        # Set multiple LED colors
        device.set_colors([
            (255, 0, 0),    # Red
            (0, 255, 0),    # Green
            (0, 0, 255)     # Blue
        ])

Note: This package provides low-level device access.
For general use, prefer the high-level interfaces in
the blinkstick.client package.
"""
