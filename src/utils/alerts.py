import os
import requests

def send_trade_alert(ticker: str, stance: str, position_size: float, final_val: float):
    webhook_url = os.getenv("ALERT_WEBHOOK_URL")
    if not webhook_url:
        return
    payload = {
        "text": f"🚨 *Investment Committee Signal Dispatched*\n"
                f"• *Ticker:* {ticker}\n"
                f"• *Stance:* {stance}\n"
                f"• *Allocation:* {position_size}%\n"
                f"• *Backtested Portfolio Value:* ${final_val:,.2f}"
    }
    try:
        requests.post(webhook_url, json=payload, timeout=5)
    except Exception as e:
        print(f"Failed to dispatch webhook alert: {e}")