from pathlib import Path
from typing import Optional


def send_notification_tool(
    email: Optional[str],
    slack_channel: Optional[str],
    report_path: Path
) -> None:
    """
    Notification stub for report delivery.
    """
    msg = f"Report generated at: {str(report_path)}"

    if email:
        print(f"[EMAIL → {email}] {msg}")

    if slack_channel:
        print(f"[SLACK → {slack_channel}] {msg}")

    if not email and not slack_channel:
        print(f"[NOTIFY] {msg}")