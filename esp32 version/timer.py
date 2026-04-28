import ctypes
import sys
import os
from pynput import mouse

# --- 1. DYNAMIC C-LIBRARY LOADER ---
if sys.platform == "win32":
    lib_filename = "precise_timer.dll"
elif sys.platform == "darwin":  
    lib_filename = "precise_timer.dylib"
else:
    lib_filename = "precise_timer.so"   

lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), lib_filename)

try:
    timer_lib = ctypes.CDLL(lib_path)
    print(f"Loaded precision timer library: {lib_filename}", flush=True)    
except OSError as e:
    print(f"Failed to load the timer library at {lib_path}", flush=True)
    print(f"Error: {e}", flush=True)
    sys.exit(1)

# --- 2. DEFINE C-TYPES 
timer_lib.timer_init.restype = ctypes.c_int
timer_lib.timer_ticks.restype = ctypes.c_longlong
timer_lib.timer_delta_us.argtypes = [ctypes.c_longlong, ctypes.c_longlong]
timer_lib.timer_delta_us.restype = ctypes.c_double

if not timer_lib.timer_init():
    print("Warning: High-resolution hardware timer failed to initialize.", flush=True)
    sys.exit(1)

# --- 3. HARDWARE EVENT LISTENER 
click_times = []
output_lines = []

def on_click(x, y, button, pressed):
    # Filter for the ESP32's Forward click (ignores your normal left/right/middle clicks)
    if pressed and button not in (mouse.Button.left, mouse.Button.right, mouse.Button.middle):
        # 1. Immediately grab the hardware tick to minimize software overhead
        ticks = timer_lib.timer_ticks()
        click_times.append(ticks)
        
        if len(click_times) > 1:
            # 2. Safely calculate the interval using the C library's math
            delta_us = timer_lib.timer_delta_us(click_times[-2], click_times[-1])
            
            # 3. Calculate deviation from the 1,000,000 µs ground truth
            drift_us = delta_us - 1000000.0
            line = f"Sample {len(click_times)-1:3d} | Interval: {delta_us:10.2f} µs | Deviation: {drift_us:8.2f} µs"
            print(line, flush=True)
            output_lines.append(line)
            
            # Stop the listener automatically after 30 interval samples
            if len(output_lines) >= 30:
                return False

# --- 4. EXECUTION LOOP ---
if __name__ == "__main__":
    print("-" * 60, flush=True)
    print("Starting cross-platform hardware validation...", flush=True)
    print("Plug in the microcontroller. Listening for HID clicks...", flush=True)
    print("Will automatically stop after 30 samples.", flush=True)
    print("Press Ctrl+C to stop the experiment early.", flush=True)
    print("-" * 60, flush=True)
    
    # Blocks the main thread and listens for OS interrupts
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()
        
    # Save the output to the specified text file
    output_file_path = r"C:\Users\alich\Downloads\precise timer\esp32 version\output.txt"
    print("-" * 60, flush=True)
    print(f"Saving output to: {output_file_path}", flush=True)
    try:
        with open(output_file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(output_lines) + "\n")
        print("File saved successfully!", flush=True)
    except Exception as e:
        print(f"Error saving to file: {e}", flush=True)