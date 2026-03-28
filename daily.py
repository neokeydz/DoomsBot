import pyautogui
import pygetwindow as gw
import time
import keyboard
import sys
import os

# --- Path Handling ---
if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

# Global control variables
RUNNING = False  # The master switch

# --- Configuration ---
WINDOW_TITLE = "Doomsday" 
CONFIDENCE_LEVEL = 0.8
IMAGE_DIR = os.path.join(base_path, "assets", "daily")
TEMPLATE_FILES = ["confirm.png", "x_icon.png", "help.png", "region.png"]

COORDINATE_GROUPS = [
    [(130, 90), (1055, 200), (750, 600), (1160, 110)],
    [(799, 644), (208, 375), (150, 640), (70, 640)], 
    [(547, 502), (841, 502), (1133, 502)],           
    [(1190, 365)],                                   
    [(1200, 154), (42, 71), (42, 71)]                
]

def get_dynamic_delay(speed):
    val = float(speed)
    return max(0.1, 2.1 - (val * 0.2))

def should_abort(log_func=None):
    """Checks if the script should stop immediately."""
    global RUNNING
    # Check both the global flag AND the physical ESC key
    if not RUNNING or keyboard.is_pressed('esc'):
        RUNNING = False
        msg = "🛑 [STOP] Aborting task immediately..."
        if log_func: log_func(msg)
        return True
    return False

def run_sequence_on_window(window, speed_val, log_func=None):
    if should_abort(log_func): return False
    
    current_delay = get_dynamic_delay(speed_val)
    msg = f"--> Processing Instance: {window.title}"
    if log_func: log_func(msg)

    try:
        window.activate()
        time.sleep(1) 
    except Exception:
        return True # Skip to next window

    region = (window.left, window.top, window.width, window.height)

    # 1. Template Matching
    for filename in TEMPLATE_FILES:
        if should_abort(log_func): return False  # Check before action
        
        img_path = os.path.join(IMAGE_DIR, filename)
        if not os.path.exists(img_path):
            continue

        try:
            loc = pyautogui.locateCenterOnScreen(img_path, region=region, confidence=CONFIDENCE_LEVEL)
            if loc:
                pyautogui.click(loc)
                if log_func: log_func(f"   [Image] Clicked {filename}")
                time.sleep(current_delay)
        except Exception:
            pass

    # 2. Coordinate Groups
    for group in COORDINATE_GROUPS:
        for (rel_x, rel_y) in group:
            if should_abort(log_func): return False  # Check before action
            
            abs_x = window.left + rel_x
            abs_y = window.top + rel_y
            
            pyautogui.click(abs_x, abs_y)
            if log_func: log_func(f"     [Coord] Clicked {rel_x}, {rel_y}")
            time.sleep(current_delay)
    
    return True

def main_entry(log_func=None, speed=5):
    global RUNNING
    RUNNING = True # Set to True when the GUI starts the task
    
    if log_func: log_func("=== Doomsday Automation Started ===")
    
    instances = gw.getWindowsWithTitle(WINDOW_TITLE)
    if not instances:
        if log_func: log_func("No windows found.")
        return

    for win in instances:
        if not RUNNING: break # Stop checking windows if flag is False
        
        if win.isMinimized:
            continue
            
        # If run_sequence returns False, a stop was requested
        if not run_sequence_on_window(win, speed, log_func):
            break

    RUNNING = False
    if log_func: log_func("=== Sequence Ended ===")

def stop_script():
    global RUNNING
    RUNNING = False
    print("Stop Signal Received.")