import gc

import supervisor

from eng_utils import logger

_profiles = {}
_start_times = {}


def log_free_ram(label: str = ""):
    """Log the current free RAM after forcing a garbage collection for consistent readings."""
    gc.collect()
    free = gc.mem_free()  # pyright: ignore[reportAttributeAccessIssue]
    prefix = f"[{label}] " if label else ""
    logger.info(f"{prefix}Free RAM: {free} bytes")


def register_profile(key: str):
    """Registers a named profile. Must be called before start_profile/stop_profile."""
    _profiles[key] = {"count": 0, "total": 0, "max": 0}


def start_profile(key: str):
    """Records the start time for a profile. Raises ValueError for unknown keys."""
    if key not in _profiles:
        raise ValueError(f"Profile key {repr(key)} has not been registered. Call register_profile first.")
    _start_times[key] = supervisor.ticks_ms()


def stop_profile(key: str):
    """Records the elapsed time for a profile. Raises ValueError for unknown keys."""
    if key not in _profiles:
        raise ValueError(f"Profile key {repr(key)} has not been registered. Call register_profile first.")
    elapsed = supervisor.ticks_ms() - _start_times[key]
    p = _profiles[key]
    p["count"] += 1
    p["total"] += elapsed
    if elapsed > p["max"]:
        p["max"] = elapsed


def report_all_profiles():
    """Logs a formatted table of all profiles with non-zero call counts, then resets all profiles."""
    active = {k: p for k, p in _profiles.items() if p["count"] > 0}

    if not active:
        return

    col_key   = "profile"
    col_calls = "calls"
    col_avg   = "avg(ms)"
    col_total = "total(ms)"
    col_max   = "max(ms)"

    rows = []
    for key in sorted(active):
        p = active[key]
        count = p["count"]
        total = p["total"]
        avg = total / count
        rows.append((key, str(count), f"{avg:.2f}", str(total), str(p["max"])))

    w_key   = max(len(col_key),   max(len(r[0]) for r in rows))
    w_calls = max(len(col_calls), max(len(r[1]) for r in rows))
    w_avg   = max(len(col_avg),   max(len(r[2]) for r in rows))
    w_total = max(len(col_total), max(len(r[3]) for r in rows))
    w_max   = max(len(col_max),   max(len(r[4]) for r in rows))

    def fmt(k, calls, avg, total, mx):
        return (f"  {k:<{w_key}}  {calls:>{w_calls}}  "
                f"{avg:>{w_avg}}  {total:>{w_total}}  {mx:>{w_max}}")

    separator = "  " + "-" * (w_key + w_calls + w_avg + w_total + w_max + 8)

    logger.info("")
    logger.info(fmt(col_key, col_calls, col_avg, col_total, col_max))
    logger.info(separator)
    for r in rows:
        logger.info(fmt(*r))
    logger.info("")
    log_free_ram("profile")

    for p in _profiles.values():
        p["count"] = 0
        p["total"] = 0
        p["max"] = 0
