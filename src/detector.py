"""
detector.py
Responsible for OBSERVING system state only.
Never takes remediation action — that belongs to remediator.py.
"""

import psutil
import subprocess


def check_disk_usage(mount_point="/", threshold_percent=85):
    """
    Checks disk usage for a given mount point against a threshold.
    Returns a dict describing the state — never prints or acts.
    """
    usage = psutil.disk_usage(mount_point)
    is_critical = usage.percent >= threshold_percent

    return {
        "check": "disk_usage",
        "mount_point": mount_point,
        "percent_used": usage.percent,
        "threshold": threshold_percent,
        "is_critical": is_critical,
    }


def check_service_status(service_name):
    """
    Checks whether a systemd service is currently active.
    Uses systemctl under the hood, since that's the source of truth
    for service state on this system (not psutil's job).
    """
    result = subprocess.run(
        ["systemctl", "is-active", service_name],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    status = result.stdout.strip()  # e.g. "active", "inactive", "failed"
    is_down = status != "active"

    return {
        "check": "service_status",
        "service_name": service_name,
        "status": status,
        "is_down": is_down,
    }
import psutil


def check_runaway_processes(cpu_threshold=80.0, mem_threshold=80.0):
    """
    Scans running processes for any exceeding the CPU or memory thresholds.
    Detect-only — does not kill or touch anything. Returns a dict listing
    any offending processes found.
    """
    offenders = []

    # First pass primes psutil's internal CPU-usage sampling (see note below)
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            proc.cpu_percent(interval=None)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    import time
    time.sleep(1)  # brief window so cpu_percent() has something to measure

    for proc in psutil.process_iter(['pid', 'name']):
        try:
            cpu = proc.cpu_percent(interval=None)
            mem = proc.memory_percent()
            if cpu >= cpu_threshold or mem >= mem_threshold:
                offenders.append({
                    "pid": proc.pid,
                    "name": proc.name(),
                    "cpu_percent": round(cpu, 1),
                    "mem_percent": round(mem, 1),
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return {
        "check": "runaway_processes",
        "cpu_threshold": cpu_threshold,
        "mem_threshold": mem_threshold,
        "offenders": offenders,
        "found_any": len(offenders) > 0,
    }
