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
