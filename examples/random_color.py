from blinkstick import find_first
from blinkstick.exceptions import BlinkStickException

bs = find_first()

if bs is None:
    print("Could not find any BlinkSticks")
    exit()

while True:
    try:
        print(f"Serial: {bs.serial()}")
        print(f"Manufacturer: {bs.manufacturer}")
        print(f"Description: {bs.description}")
        # print(f"Mode: {bs.get_mode()}")
        print(f"InfoBlock1: {bs.info_block1}")
        print(f"InfoBlock2: {bs.info_block2}")
        print(f"Variant: {bs.variant}")
        print(f"Variant String: {bs.variant_string}")
        while True:
            bs.set_random_color()
            print(f"Color: {bs.get_color()}")
            input("Press Enter to continue...")
    except BlinkStickException:
        print("Could not communicate with BlinkStick")
