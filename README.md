# Self-Healing Infrastructure Agent

A lightweight, zero-cost, self-healing monitoring agent for small Linux servers, written in Python. It detects common failure patterns and automatically fixes what it safely can — with full audit logging so nothing happens silently.

## Why this exists

Small teams and startups running a handful of Linux servers often can't afford enterprise tools like Datadog or PagerDuty. This project fills that gap with something simple, transparent, and auditable — closer to how a junior sysadmin would behave: detect, fix (when safe), explain what was done, escalate when it isn't.

## What it monitors

| Check | Detection | Response |
|---|---|---|
| Disk usage | psutil.disk_usage() against a configurable threshold | Attempts safe cleanup (package cache, rotated logs), re-checks, alerts only if still critical |
| Named services | systemctl is-active | Automatically restarts the service; alerts if the restart itself fails |
| Runaway processes | CPU/memory usage via psutil | Detect-only — alerts with process name/PID/usage, since auto-killing an unknown process is too risky to automate |
| Cron job health | Heartbeat-file staleness check | Detect-only — alerts if a scheduled job's heartbeat file is missing or overdue |

## Architecture

    main.py               entry point, ties everything together into one run
    src/detector.py        observes system state only, never acts
    src/remediator.py      takes remediation actions, never re-checks its own work
    src/logger.py          JSON Lines audit log (logs/audit.log) of every check + action
    src/alerter.py         Slack webhook alerting for anything the agent can't fix itself
    src/config_loader.py   loads config/config.yaml
    config/config.yaml     thresholds, monitored services, webhook URL (gitignored)

Every check writes to logs/audit.log, whether or not anything needed fixing — the goal is a complete, honest record of what the agent observed and did.

## Setup

    git clone https://github.com/AbdullahAmjad-29/self-healing-agent.git
    cd self-healing-agent
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

    cp config/config.yaml.example config/config.yaml
    # edit config/config.yaml - set your Slack webhook URL and adjust thresholds

Run it once manually:

    python3 main.py

## Running as a service

The agent is designed to run on a schedule via systemd, not as a long-lived process. See docs/incidents/05-selinux-systemd-denial.md for a real deployment issue (SELinux blocking systemd from executing the venv's Python binary) encountered and fixed while setting this up.

## Incident writeups

docs/incidents/ contains writeups of real, tested failure scenarios, each backed by actual audit-log evidence rather than hypothetical descriptions. Covers all four detectors plus one real infrastructure troubleshooting incident (SELinux).

## Security note

config/config.yaml holds a real Slack webhook URL and is gitignored. config/config.yaml.example is the safe template - copy it and fill in your own values.
