import json
import os
from datetime import datetime

# Build the log path relative to this file's location, not the current working directory.
# This means the script works correctly whether you run it from ~/self-healing-agent
# or from anywhere else (e.g. as a systemd service later).
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
LOG_FILE = os.path.join(LOG_DIR, "audit.log")


def log_event(detection_result, remediation_result=None):
    """
    Records one audit entry as a JSON line.

    detection_result: dict from a detector.py function (required)
    remediation_result: dict from a remediator.py function, or None
                         if nothing needed fixing (default: None)
    """
    os.makedirs(LOG_DIR, exist_ok=True)

    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "detection": detection_result,
        "remediation": remediation_result,
    }

    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

    return entry
