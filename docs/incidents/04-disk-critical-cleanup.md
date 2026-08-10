# Incident: Disk Usage Critical - Cleanup Attempted, Alert Escalated

**Date:** 2026-08-10
**Trigger:** Temporarily lowered `threshold_percent` in `config.yaml` to 1%, forcing normal disk usage (2.8%) to register as critical, in order to exercise the full disk-remediation path.
**Detected by:** `check_disk_usage()` in `detector.py`
**Remediation attempted by:** `clear_package_cache()` and `clear_rotated_logs()` in `remediator.py`

## What happened
Disk usage was artificially forced into the "critical" state to test the agent's disk-healing sequence: detect critical usage, attempt safe cleanup actions, re-check whether the cleanup actually helped, and only alert a human if the problem persists.

## Detection
Original critical detection, with both cleanup actions attempted:

    {"timestamp": "2026-08-10T21:01:18.961211Z", "detection": {"check": "disk_usage", "mount_point": "/", "percent_used": 2.8, "threshold": 1, "is_critical": true}, "remediation": {"cache_cleanup": {"action": "clear_package_cache", "success": true, "output": "0 files removed", "error": null}, "logs_cleanup": {"action": "clear_rotated_logs", "log_dir": "/var/log", "files_found": [], "files_deleted": [], "success": true}}}

Re-check after cleanup - still critical, since real usage never actually exceeded the artificial 1% threshold:

    {"timestamp": "2026-08-10T21:01:18.961531Z", "detection": {"check": "disk_usage", "mount_point": "/", "percent_used": 2.8, "threshold": 1, "is_critical": true}, "remediation": null}

## Response
The agent attempted both safe, regenerable cleanup actions automatically (package cache clearing, rotated log deletion) before considering escalation. Both cleanup actions succeeded, but since the underlying "critical" condition was artificial (the threshold was intentionally set below real usage, not real disk exhaustion), the re-check still showed critical. The agent correctly proceeded to send a Slack alert.

## Outcome
Escalated to human after automated remediation was attempted and confirmed insufficient. This demonstrates the intended behavior: the agent tries safe fixes first, verifies whether they worked, and only bothers a human when its own actions didn't resolve the issue - rather than either alerting on every critical reading or silently giving up.

## Evidence
- Audit log entries above (logs/audit.log)
- Slack alert confirmed delivered to #new-channel: "Disk still critical... after cleanup attempt"
