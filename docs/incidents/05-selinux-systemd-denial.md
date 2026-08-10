# Incident: SELinux Blocked systemd From Executing the Agent

**Date:** 2026-08-10
**Trigger:** Real issue encountered while packaging the agent as a systemd service - not simulated.
**Symptom:** `systemctl start self-healing-agent.service` failed immediately with `status=203/EXEC`.

## What happened
The systemd unit pointed at `venv/bin/python3` inside the project's home-directory virtual environment. Running the exact same command manually as the `sentinel_admin` user worked fine, but running it via systemd failed immediately with an EXEC error, despite file permissions on the full path chain being correct.

## Diagnosis
`getenforce` confirmed SELinux was in `Enforcing` mode. Checking the audit log directly identified the real cause:

    sudo ausearch -m avc -ts recent

This showed an AVC (Access Vector Cache) denial: systemd's `init_t` security context was denied `read` access to the `python3` symlink inside `venv/bin`, because that file was labeled `user_home_t` (ordinary home-directory content) rather than an executable-binary type. SELinux enforces this distinction regardless of standard Unix file permissions - `rwx` bits being correct doesn't matter if the SELinux label doesn't permit the access.

## Fix
Relabeled the venv's `bin/` directory to use the `bin_t` SELinux type, which systemd-launched processes are permitted to execute:

    sudo semanage fcontext -a -t bin_t "/home/sentinel_admin/self-healing-agent/venv/bin(/.*)?"
    sudo restorecon -Rv /home/sentinel_admin/self-healing-agent/venv/bin

## Outcome
Resolved. `systemctl start self-healing-agent.service` subsequently succeeded (`status=0/SUCCESS`), with the full agent run visible in `journalctl`/`systemctl status` output.

## Why this matters
This is a common, realistic obstacle when running Python virtual environments as systemd services on SELinux-enforcing systems (RHEL/CentOS family) - and a good example of why "check file permissions" isn't always enough; SELinux operates as a second, independent access-control layer on top of standard Unix permissions.
