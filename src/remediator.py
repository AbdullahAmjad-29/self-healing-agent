
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
