import ctypes
import sys
import os
import time

# --- 1. LOAD THE MAC C-LIBRARY ---
lib_filename = "precise_timer.dylib"
lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), lib_filename)

try:
    timer_lib = ctypes.CDLL(lib_path)
except OSError as e:
    print(f"Failed to load {lib_filename}. Make sure it is compiled and in the same folder.")
    sys.exit(1)

# --- 2. DEFINE C-TYPES ---
timer_lib.timer_init.restype = ctypes.c_int
timer_lib.timer_ticks.restype = ctypes.c_longlong
timer_lib.timer_delta_us.argtypes = [ctypes.c_longlong, ctypes.c_longlong]
timer_lib.timer_delta_us.restype = ctypes.c_double

# Initialize the Mach timer
if not timer_lib.timer_init():
    print("Error: mach_absolute_time failed to initialize.")
    sys.exit(1)

# --- 3. TEST MACH_ABSOLUTE_TIME ---
print("Benchmarking mach_absolute_time() resolution...")
print("-" * 50)

# A synthetic delay of 10 milliseconds
target_sleep_s = 0.010 

# Capture starting raw Mach ticks
start_ticks = timer_lib.timer_ticks()

# Execute the delay
time.sleep(target_sleep_s)

# Capture ending raw Mach ticks
end_ticks = timer_lib.timer_ticks()

# Calculate the difference in raw CPU ticks
raw_tick_difference = end_ticks - start_ticks

# Pass the raw ticks to the C library to safely convert to microseconds
# using the (ticks * numerator / denominator) formula
converted_us = timer_lib.timer_delta_us(start_ticks, end_ticks)
converted_ms = converted_us / 1000.0

print(f"Target Delay:       {target_sleep_s * 1000:.2f} ms")
print(f"Raw Mach Ticks:     {raw_tick_difference:,}")
print(f"Converted Time:     {converted_ms:.4f} ms ({converted_us:.2f} µs)")
print("-" * 50)