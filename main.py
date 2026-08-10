from src.detector import check_disk_usage, check_service_status
from src.remediator import restart_service
from src.logger import log_event

# Services to monitor — will move to config.yaml later
MONITORED_SERVICES = ["sshd", "cockpit.socket"]


def run_checks():
    print("=== Self-Healing Agent — Run Started ===")

    # --- Disk check ---
    disk_result = check_disk_usage()
    print(f"[Disk] {disk_result['percent_used']}% used (threshold {disk_result['threshold']}%)")
    log_event(disk_result, None)
    # Note: no remediation wired up for disk yet — clear_package_cache/
    # clear_rotated_logs from remediator.py aren't hooked in here yet,
    # that's Phase 3 work. For now we just detect and log.

    # --- Service checks ---
    for service in MONITORED_SERVICES:
        result = check_service_status(service)
        print(f"[Service: {service}] status={result['status']}")

        remediation = None
        if result["is_down"]:
            print(f"  -> {service} is down, attempting restart...")
            remediation = restart_service(service)
            print(f"  -> Restart success: {remediation['success']}")

        log_event(result, remediation)

    print("=== Self-Healing Agent — Run Complete ===")


if __name__ == "__main__":
    run_checks()
