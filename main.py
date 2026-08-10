from src.detector import check_disk_usage, check_service_status
from src.remediator import restart_service
from src.logger import log_event
from src.config_loader import load_config
from src.alerter import send_alert


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

    if disk_result["is_critical"]:
        alert_msg = (
            f"🚨 Disk critical on {disk_result['mount_point']}: "
            f"{disk_result['percent_used']}% used (threshold {disk_result['threshold']}%). "
            f"No automated remediation available yet."
        )
        print("  -> Disk critical, no remediation available. Sending alert...")
        send_alert(alert_msg)

    # --- Service checks ---
    for service in config["services"]:
        result = check_service_status(service)
        print(f"[Service: {service}] status={result['status']}")

        remediation = None
        if result["is_down"]:
            print(f"  -> {service} is down, attempting restart...")
            remediation = restart_service(service)
            print(f"  -> Restart success: {remediation['success']}")

            if not remediation["success"]:
                alert_msg = (
                    f"🚨 Failed to restart {service}: {remediation['error']}. "
                    f"Manual intervention needed."
                )
                print("  -> Restart failed. Sending alert...")
                send_alert(alert_msg)

        log_event(result, remediation)

    print("=== Self-Healing Agent — Run Complete ===")


if __name__ == "__main__":
    run_checks()
