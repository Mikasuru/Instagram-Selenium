import json
import logging
import requests
from datetime import datetime

from config import SuccessEmb, ErrorEmb

def SendNoti(webhook_url: str, TargetName: str, FollowersList: list[str] | None, ErrorMsg: str | None = None) -> None:
    if not webhook_url or "YOUR_DISCORD_WebhookUrl_HERE" in webhook_url:
        logging.warning("Webhook URL not provided. Skipping notification.")
        return

    headers = {"Content-Type": "application/json"}
    
    if ErrorMsg:
        embed = CreateError(TargetName, ErrorMsg)
    else:
        embed = CreateSuccess(TargetName, FollowersList)

    payload = {"embeds": [embed]}

    try:
        logging.info("Sending result to Discord webhook...")
        response = requests.post(webhook_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        logging.info("Webhook sent successfully!")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to send webhook: {e}")

def CreateSuccess(TargetName: str, FollowersList: list[str]) -> dict:
    description_header = f"**Successfully fetched {len(FollowersList)} followers for `{TargetName}`**\n\n"
    
    follower_lines = []
    char_count = len(description_header)
    
    for i, follower in enumerate(FollowersList, 1):
        line = f"{i}. {follower}\n"
        if char_count + len(line) > 4000:
            follower_lines.append(f"...and {len(FollowersList) - (i-1)} more.")
            break
        follower_lines.append(line)
        char_count += len(line)
    
    return {
        "title": "Instagram Follower Scrape Report",
        "description": description_header + "".join(follower_lines),
        "color": SuccessEmb,
        "footer": {"text": "Scrape Completed"},
        "timestamp": datetime.utcnow().isoformat()
    }

def CreateError(TargetName: str, ErrorMsg: str) -> dict:
    return {
        "title": f"Scrape Failed: {TargetName}",
        "description": f"An error occurred while scraping followers.\n\n**Error:**\n```{ErrorMsg}```",
        "color": ErrorEmb,
        "timestamp": datetime.utcnow().isoformat()
    }