# Incident: Runaway Process Detected (CPU)

**Date:** 2026-08-10
**Trigger:** Manually spawned a deliberate CPU-hogging process (`yes > /dev/null &`) to simulate a stuck or misbehaving process consuming excessive CPU.
**Detected by:** `check_runaway_processes()` in `detector.py`

## What happened
A background process (`yes`) was intentionally started to loop indefinitely, consuming a full CPU core. This simulates a real-world scenario such as a stuck script, an infinite loop in application code, or a leaked worker process quietly degrading server performance.

## Detection
Clean baseline immediately before the test - no offenders:

    {"timestamp": "2026-08-10T21:09:21.284593Z", "detection": {"check": "runaway_processes", "cpu_threshold": 80.0, "mem_threshold": 80.0, "offenders": [], "found_any": false}, "remediation": null}

Same check, run again moments later with the `yes` process active - correctly flagged:

    {"timestamp": "2026-08-10T21:09:28.557851Z", "detection": {"check": "runaway_processes", "cpu_threshold": 80.0, "mem_threshold": 80.0, "offenders": [{"pid": 10321, "name": "yes", "cpu_percent": 105.3, "mem_percent": 0.1}], "found_any": true}, "remediation": null}

## Response
The agent does not attempt to kill offending processes automatically. This is a deliberate design decision: an automated agent killing an unfamiliar process is genuinely risky - it could be a legitimate heavy job, not an actual problem. Instead, the agent sent a Slack alert identifying the specific process (name, PID, CPU%, memory%), so a human can make an informed decision.

## Outcome
Escalated to human, by design. The process was manually terminated (`kill %1`) once the test was confirmed successful, and a follow-up check confirmed the system returned to a clean baseline.

## Evidence
- Audit log entries above (logs/audit.log)
- Slack alert confirmed delivered to #new-channel, listing the offending process by name and PID
