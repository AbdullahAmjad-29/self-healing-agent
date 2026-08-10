
"""
remediator.py
Responsible for TAKING ACTION based on what detector.py reports.
Every action returns a result describing what was done — never acts silently.
"""

import subprocess


def restart_service(service_name):
    """
    Attempts to restart a systemd service.
    Should only be called when detector.py has already confirmed
    the service is down — this function does not check status itself.
    """
    result = subprocess.run(
        ["sudo", "systemctl", "restart", service_name],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    success = result.returncode == 0

    return {
        "action": "restart_service",
        "service_name": service_name,
        "success": success,
        "error": result.stderr.strip() if not success else None,
    }
def clear_package_cache():
    """
    Clears the dnf/yum package manager cache.
    This is always safe to remove — it's fully regenerable and never
    required for the system to keep running.
    """
    result = subprocess.run(
        ["sudo", "dnf", "clean", "all"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    success = result.returncode == 0

    return {
        "action": "clear_package_cache",
        "success": success,
        "output": result.stdout.strip(),
        "error": result.stderr.strip() if not success else None,
    }


def clear_rotated_logs(log_dir="/var/log"):
    """
    Removes already-rotated (compressed) log files, e.g. messages-20250101.gz.
    Never touches a live log file that's still being actively written to —
    only files ending in .gz, which systemd's logrotate has already archived.
    """
    result = subprocess.run(
        ["sudo", "find", log_dir, "-name", "*.gz", "-type", "f"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    files_found = [f for f in result.stdout.strip().split("\n") if f]

    deleted = []
    for f in files_found:
        del_result = subprocess.run(
            ["sudo", "rm", "-f", f],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        if del_result.returncode == 0:
            deleted.append(f)

    return {
        "action": "clear_rotated_logs",
        "log_dir": log_dir,
        "files_found": files_found,
        "files_deleted": deleted,
        "success": len(deleted) == len(files_found),
    }
