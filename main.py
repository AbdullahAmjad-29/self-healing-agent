from src.detector import check_disk_usage, check_service_status, check_runaway_processes
from src.remediator import restart_service, clear_package_cache, clear_rotated_logs
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

    disk_remediation = None
    if disk_result["is_critical"]:
        print("  -> Disk critical. Attempting cleanup...")
        cache_result = clear_package_cache()
        logs_result = clear_rotated_logs()
        disk_remediation = {"cache_cleanup": cache_result, "logs_cleanup": logs_result}
        print(f"  -> Cache cleanup: {cache_result['success']}, Logs cleanup: {logs_result['success']}")

    log_event(disk_result, disk_remediation)

    if disk_result["is_critical"]:
        recheck = check_disk_usage(
            mount_point=config["disk"]["mount_point"],
            threshold_percent=config["disk"]["threshold_percent"],
        )
        print(f"  -> Re-checked disk after cleanup: {recheck['percent_used']}% used")
        log_event(recheck, None)

        if recheck["is_critical"]:
            alert_msg = (
                f"🚨 Disk still critical on {recheck['mount_point']} after cleanup attempt: "
                f"{recheck['percent_used']}% used (threshold {recheck['threshold']}%). "
                f"Manual intervention needed."
            )
            print("  -> Still critical after cleanup. Sending alert...")
            send_alert(alert_msg)
        else:
            print("  -> Cleanup resolved the issue. No alert needed.")

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

    # --- Runaway process check ---
    process_result = check_runaway_processes(
        cpu_threshold=config["processes"]["cpu_threshold"],
        mem_threshold=config["processes"]["mem_threshold"],
    )
    print(f"[Processes] Offenders found: {process_result['found_any']}")
    log_event(process_result, None)

    if process_result["found_any"]:
        offender_lines = "\n".join(
            f"  • {p['name']} (PID {p['pid']}): {p['cpu_percent']}% CPU, {p['mem_percent']}% MEM"
            for p in process_result["offenders"]
        )
        alert_msg = (
            f"🚨 Runaway process(es) detected:\n{offender_lines}\n"
            f"No automated action taken — review manually."
        )
        print("  -> Runaway process(es) found. Sending alert...")
        send_alert(alert_msg)

    print("=== Self-Healing Agent — Run Complete ===")


if __name__ == "__main__":
    run_checks()
