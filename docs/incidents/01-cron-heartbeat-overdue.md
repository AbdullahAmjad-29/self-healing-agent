# Incident: Cron Heartbeat Overdue

**Date:** 2026-08-10
**Trigger:** Simulated by temporarily lowering `max_age_minutes` in `config.yaml` to an unreasonably strict value (0.01 min), forcing a real, actively-updating heartbeat file to register as overdue.
**Detected by:** `check_cron_heartbeat()` in `detector.py`

## What happened
A cron job runs every minute, touching a heartbeat file (`heartbeats/test-job.heartbeat`) on success. To simulate a scenario where a scheduled job silently stops running (e.g. a cron entry gets removed, or the job starts failing), the allowed staleness threshold was temporarily set far below the job's actual interval, so the agent would treat a normally-healthy heartbeat as overdue.

## Detection
Healthy baseline, prior run - heartbeat well within tolerance:

    {"timestamp": "2026-08-10T21:16:34.738062Z", "detection": {"check": "cron_heartbeat", "heartbeat_file": "/home/sentinel_admin/self-healing-agent/heartbeats/test-job.heartbeat", "max_age_minutes": 5, "exists": true, "age_minutes": 0.6, "is_overdue": false}, "remediation": null}

Simulated failure - same heartbeat file, tighter threshold, correctly flagged:

    {"timestamp": "2026-08-10T21:17:03.986030Z", "detection": {"check": "cron_heartbeat", "heartbeat_file": "/home/sentinel_admin/self-healing-agent/heartbeats/test-job.heartbeat", "max_age_minutes": 0.01, "exists": true, "age_minutes": 1.0, "is_overdue": true}, "remediation": null}

## Response
There is no automated remediation for a failed cron job - the agent cannot safely determine why a scheduled job stopped running or re-trigger it without risk. Instead, the agent sent a Slack alert via the incoming webhook, escalating directly to a human for investigation.

## Outcome
Escalated to human, by design. This detector is intentionally alert-only, consistent with the project's approach to remediation: the agent only acts automatically when the action is safe and well-understood (restarting a known service, clearing regenerable cache/log files). Anything requiring judgment - like why a scheduled job failed - goes to a person.

## Evidence
- Audit log entries above (logs/audit.log)
- Slack alert confirmed delivered to #new-channel in the self-healing-agent Slack workspace
