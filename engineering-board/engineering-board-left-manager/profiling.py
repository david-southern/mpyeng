import gc

import supervisor

from eng_utils import logger

_profiles = {}
_active_count = 0
_last_report_time = None

_COUNT = 0  # count
_TOTAL = 1  # total ms
_MAX = 2  # max ms
_OVERLAP = 3  # overlapping flag
_START = 4  # start time (None when not active)
_KEY = 5    # profile name string (for error messages and report)

# Cache the ticks_ms function reference to avoid repeated attribute lookups
_ticks_ms = supervisor.ticks_ms


def log_free_ram(label: str = ""):
    """Log the current free RAM after forcing a garbage collection for consistent readings."""
    gc.collect()
    free = gc.mem_free()  # pyright: ignore[reportAttributeAccessIssue]
    prefix = f"[{label}] " if label else ""
    logger.info(f"{prefix}Free RAM: {free} bytes")


def register_profile(key: str) -> list:
    """Registers a named profile and returns a handle for use with start_profile/stop_profile."""
    handle = [0, 0, 0, False, None, key]  # [count, total, max, overlapping, start_time, key]
    _profiles[key] = handle
    return handle


def start_profile(handle: list):
    """Records the start time for a profile handle. Raises ValueError if already active. Flags the
    profile as overlapping if any other profile is currently active. NOTE: Each call to
    start_profile takes approx 0.04ms - not a lot for basic profiling, but if you're profiling
    inside a tight loop, it can add up. """
    global _active_count
    if handle[_START] is not None:
        raise ValueError(f"Profile {repr(handle[_KEY])} is already active. Call stop_profile before starting again.")
    if _active_count:
        handle[_OVERLAP] = True
    _active_count += 1
    handle[_START] = _ticks_ms()


def stop_profile(handle: list):
    """Records the elapsed time for a profile handle. Raises ValueError if not active. NOTE: Each
    call to start_profile takes approx 0.04ms - not a lot for basic profiling, but if you're
    profiling inside a tight loop, it can add up. """
    global _active_count
    start = handle[_START]
    if start is None:
        raise ValueError(f"Profile {repr(handle[_KEY])} is not active. Call start_profile before stopping.")
    elapsed = _ticks_ms() - start
    handle[_START] = None
    _active_count -= 1
    handle[_COUNT] += 1
    handle[_TOTAL] += elapsed
    if elapsed > handle[_MAX]:
        handle[_MAX] = elapsed


def report_all_profiles():
    """Logs a formatted table of all profiles with non-zero call counts, then resets all profiles."""
    global _last_report_time

    now = _ticks_ms()

    # Stop any profiles that are currently running; remember them to restart after reset
    active_at_report = [k for k, p in _profiles.items() if p[_START] is not None]
    for key in active_at_report:
        stop_profile(_profiles[key])

    active = {k: p for k, p in _profiles.items() if p[_COUNT] > 0}

    if not active:
        _last_report_time = now
        # Restart any profiles that were stopped
        for key in active_at_report:
            start_profile(_profiles[key])
        return

    col_key   = "profile"
    col_calls = "calls"
    col_avg   = "avg(ms)"
    col_total = "total(ms)"
    col_max   = "max(ms)"

    rows = []
    for key in sorted(active):
        p = active[key]
        count = p[_COUNT]
        total = p[_TOTAL]
        avg = total / count
        label = f"{key}*" if p[_OVERLAP] else key
        rows.append((label, str(count), f"{avg:.2f}", str(total), str(p[_MAX])))

    # Compute totals / averages using only non-overlapping profiles
    non_overlapping = [(key, p) for key, p in active.items() if not p[_OVERLAP]]
    if non_overlapping:
        sum_calls = sum(p[_COUNT] for _, p in non_overlapping)
        sum_total = sum(p[_TOTAL] for _, p in non_overlapping)
        avg_avg   = sum(p[_TOTAL] / p[_COUNT] for _, p in non_overlapping) / len(non_overlapping)
    else:
        sum_calls = 0
        sum_total = 0
        avg_avg   = 0.0
    total_row = ("Total", str(sum_calls), f"{avg_avg:.2f}", str(sum_total), "")

    # Compute idle row
    observed_ms = (now - _last_report_time) if _last_report_time is not None else 0
    idle_ms = max(0, observed_ms - sum_total)
    idle_row = ("Idle", "", "", str(idle_ms), str(observed_ms))

    w_key   = max(len(col_key),   max(len(r[0]) for r in rows), len("Total"), len("Idle"))
    w_calls = max(len(col_calls), max(len(r[1]) for r in rows), len(total_row[1]))
    w_avg   = max(len(col_avg),   max(len(r[2]) for r in rows), len(total_row[2]))
    w_total = max(len(col_total), max(len(r[3]) for r in rows), len(total_row[3]), len(idle_row[3]))
    w_max   = max(len(col_max),   max(len(r[4]) for r in rows), len(idle_row[4]))

    def fmt(k, calls, avg, total, mx):
        return (f"  {k:<{w_key}}  {calls:>{w_calls}}  "
                f"{avg:>{w_avg}}  {total:>{w_total}}  {mx:>{w_max}}")

    separator = "  " + "-" * (w_key + w_calls + w_avg + w_total + w_max + 8)

    logger.info("")
    logger.info(fmt(col_key, col_calls, col_avg, col_total, col_max))
    logger.info(separator)
    for r in rows:
        logger.info(fmt(*r))
    logger.info(separator)
    logger.info(fmt(*total_row))
    logger.info(fmt(*idle_row))
    logger.info("")
    log_free_ram("profile")

    _last_report_time = now

    for p in _profiles.values():
        p[_COUNT] = 0
        p[_TOTAL] = 0
        p[_MAX] = 0
        p[_OVERLAP] = False
        # p[_START] is already None (all active profiles were stopped above)

    # Restart any profiles that were stopped before the report
    for key in active_at_report:
        start_profile(_profiles[key])
