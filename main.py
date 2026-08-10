from src.detector import check_disk_usage, check_service_status
from src.remediator import restart_service
from src.logger import log_event
from src.config_loader import load_config


def run_checks():
    config = load_config()
    print("=== Self-Healing Agent — Run Started ===")

    # --- Disk check ---
    disk_result = check_disk_usage(
        mount_point=config["disk"]["mount_point"],
        threshold_percent=config["disk"]["threshold_percent"],
    )
    print(f"[Disk] {disk_result['percent_used']}% used (threshold {disk_result['threshold']}%)")
    log_event(disk_result, None)

    # --- Service checks ---
    for service in config["services"]:
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
