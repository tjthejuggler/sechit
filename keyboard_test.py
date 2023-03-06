from evdev import InputDevice, list_devices, ecodes

def find_keyboard_device():
    # Loop through all input devices and find the one with type EV_KEY
    for device_path in list_devices():
        device = InputDevice(device_path)
        for event_type, event_codes in device.capabilities().items():
            if ecodes.EV_KEY in event_codes:
                # Return the device ID of the first keyboard device found
                return device_path[-1]
    return None

def input_with_device():
    keyboard_id = find_keyboard_device()
    if keyboard_id is None:
        print("No keyboard device found")
        return None

    # Prompt the user for input and return it along with the device ID
    user_input = input(f"Enter text using keyboard {keyboard_id}: ")
    return user_input, keyboard_id

user_input, keyboard_id = input_with_device()
print(f"You typed '{user_input}' using keyboard {keyboard_id}")
