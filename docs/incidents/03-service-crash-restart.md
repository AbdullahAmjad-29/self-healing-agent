# Incident: Service Crash and Automatic Restart

**Date:** 2026-08-10
**Trigger:** Manually stopped a monitored service (`sudo systemctl stop cockpit.socket`) to simulate a real service crash.
**Detected by:** `check_service_status()` in `detector.py`
**Remediated by:** `restart_service()` in `remediator.py`

## What happened
A monitored service, `cockpit.socket`, was manually stopped to simulate an unexpected crash. This is the most common failure mode a self-healing agent should catch and fix without human involvement.

## Detection
Healthy baseline immediately before the test:

    {"timestamp": "2026-08-10T20:32:28.111152Z", "detection": {"check": "service_status","service_name": "cockpit.socket", "status": "active", "is_down": false}, "remediation": null}

Service stopped, detected as down, and automatically restarted:

    {"timestamp": "2026-08-10T20:33:36.961905Z", "detection": {"check": "service_status","service_name": "cockpit.socket", "status": "inactive", "is_down": true}, "remediation": {"action": "restart_service", "service_name": "cockpit.socket", "success": true, "error": null}}

## Response
Unlike a runaway process or a failed cron job, restarting a specifically named, monitored service is a safe and well-understood action. The agent restarted `cockpit.socket` automatically via `systemctl restart`, with no human intervention required.

## Outcome
Resolved automatically. Subsequent checks throughout the rest of testing consistently showed `cockpit.socket` back to `status: active`, confirming the restart held and the service did not immediately crash again.

## Evidence
- Audit log entries above (logs/audit.log)
- Later audit log entries (e.g. 20:37:01, 20:40:54) confirm the service remained healthy after the automated restart
