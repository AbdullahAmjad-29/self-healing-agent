import requests
from src.config_loader import load_config


def send_alert(message):
    """
    Sends a plain-text alert to the configured Slack webhook.
    Returns a result dict describing success/failure — never raises,
    so a broken webhook can't crash the agent's main loop.
    """
    config = load_config()
    webhook_url = config.get("alerting", {}).get("slack_webhook_url")

    if not webhook_url or "PASTE_YOUR" in webhook_url:
        return {"success": False, "error": "Slack webhook URL not configured"}

    try:
        response = requests.post(webhook_url, json={"text": message}, timeout=5)
        response.raise_for_status()
        return {"success": True, "error": None}
    except requests.RequestException as e:
        return {"success": False, "error": str(e)}
