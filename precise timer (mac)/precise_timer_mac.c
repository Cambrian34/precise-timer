#include <mach/mach_time.h>
#include <stdint.h>

static uint64_t _origin = 0;
static mach_timebase_info_data_t _timebase = {0};
static int _ready = 0;

__attribute__((visibility("default"))) int timer_init(void) {
    if (mach_timebase_info(&_timebase) == KERN_SUCCESS) {
        _origin = mach_absolute_time();
        _ready = 1;
        return 1;
    }
    return 0;
}

__attribute__((visibility("default"))) long long timer_freq_hz(void) {
    if (!_ready) return 0LL;
    // Frequency = 1e9 * (denominator / numerator)
    return (long long)((1000000000ULL * _timebase.denom) / _timebase.numer);
}

__attribute__((visibility("default"))) long long timer_ticks(void) {
    if (!_ready) return -1LL;
    return (long long)(mach_absolute_time() - _origin);
}

__attribute__((visibility("default"))) double timer_seconds(void) {
    if (!_ready) return -1.0;
    uint64_t ticks = mach_absolute_time() - _origin;
    // Convert ticks to nanoseconds, then to seconds
    double nsec = (double)ticks * (double)_timebase.numer / (double)_timebase.denom;
    return nsec / 1000000000.0;
}

__attribute__((visibility("default"))) double timer_microseconds(void) {
    if (!_ready) return -1.0;
    uint64_t ticks = mach_absolute_time() - _origin;
    // Convert ticks to nanoseconds, then to microseconds
    double nsec = (double)ticks * (double)_timebase.numer / (double)_timebase.denom;
    return nsec / 1000.0;
}

__attribute__((visibility("default"))) double timer_delta_us(long long t_start, long long t_end) {
    if (!_ready) return -1.0;
    uint64_t delta_ticks = (uint64_t)(t_end - t_start);
    double nsec = (double)delta_ticks * (double)_timebase.numer / (double)_timebase.denom;
    return nsec / 1000.0;
}