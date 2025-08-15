import requests
import logging
import json
from typing import Optional
from src.config import DISCORD_WEBHOOK_URL, DRY_RUN, MAX_RETRIES, RETRY_DELAY
import time

logger = logging.getLogger(__name__)


class DiscordPoster:
    def __init__(self):
        """Initialize Discord poster."""
        self.webhook_url = DISCORD_WEBHOOK_URL
        if not self.webhook_url:
            logger.warning("Discord webhook URL not configured")
    
    def format_discord_message(self, analysis: str, title: str, url: str) -> str:
        """
        Format message for Discord.
        
        Args:
            analysis: AI analysis text
            title: Article title
            url: Article URL
            
        Returns:
            Formatted Discord message
        """
        message = f"""🔥 **New drop from the threat trenches** 🔥

**#TodayInThreats 🔍 | {title}**

Every day, we dig into a new threat report and break it down with the PEAK Framework – so you can hunt smarter, faster, and louder.

{analysis}

[Read Full Report]({url})"""
        
        # Ensure message doesn't exceed Discord limit (2000 chars)
        if len(message) > 2000:
            # Calculate how much we need to trim from analysis
            excess = len(message) - 2000
            analysis_limit = len(analysis) - excess - 50  # Extra buffer
            
            if analysis_limit > 100:  # Only trim if we'll have meaningful content left
                analysis = analysis[:analysis_limit].rsplit('.', 1)[0] + '...'
                message = f"""🔥 **New drop from the threat trenches** 🔥

**#TodayInThreats 🔍 | {title}**

Every day, we dig into a new threat report and break it down with the PEAK Framework – so you can hunt smarter, faster, and louder.

{analysis}

[Read Full Report]({url})"""
        
        return message
    
    def post_to_discord(self, analysis: str, title: str, url: str) -> bool:
        """
        Send formatted message to Discord webhook.
        
        Args:
            analysis: AI analysis text
            title: Article title
            url: Article URL
            
        Returns:
            True if posted successfully, False otherwise
        """
        if not self.webhook_url or DRY_RUN:
            logger.info(f"Skipping Discord post (dry_run={DRY_RUN}, webhook={bool(self.webhook_url)})")
            if DRY_RUN:
                message = self.format_discord_message(analysis, title, url)
                logger.info(f"[DRY RUN] Would post to Discord:\n{message[:500]}...")
            return True
        
        # Format message
        message = self.format_discord_message(analysis, title, url)
        
        # Prepare payload
        payload = {
            "content": message,
            "username": "Threat Intel Bot",
            "avatar_url": "https://i.imgur.com/4M34hi2.png"  # Optional: bot avatar
        }
        
        # Attempt to post with retries
        for attempt in range(MAX_RETRIES):
            try:
                logger.info(f"Posting to Discord (attempt {attempt + 1}/{MAX_RETRIES})")
                
                response = requests.post(
                    self.webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                
                if response.status_code == 204:
                    logger.info("Successfully posted to Discord")
                    return True
                elif response.status_code == 429:
                    # Rate limited
                    retry_after = response.json().get('retry_after', RETRY_DELAY)
                    logger.warning(f"Rate limited, retrying after {retry_after} seconds")
                    time.sleep(retry_after)
                else:
                    logger.error(f"Discord API returned status code: {response.status_code}")
                    logger.error(f"Response: {response.text}")
                    
            except Exception as e:
                logger.error(f"Error posting to Discord (attempt {attempt + 1}): {e}")
            
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
        
        logger.error(f"Failed to post to Discord after {MAX_RETRIES} attempts")
        return False
    
    def send_error_notification(self, error_msg: str) -> bool:
        """
        Send error notification to Discord.
        
        Args:
            error_msg: Error message to send
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.webhook_url or DRY_RUN:
            logger.info(f"Skipping error notification (dry_run={DRY_RUN}, webhook={bool(self.webhook_url)})")
            return True
        
        payload = {
            "content": f"⚠️ **Threat Intel Bot Error** ⚠️\n\n{error_msg}",
            "username": "Threat Intel Bot",
            "avatar_url": "https://i.imgur.com/4M34hi2.png"
        }
        
        try:
            logger.info("Sending error notification to Discord")
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 204:
                logger.info("Error notification sent successfully")
                return True
            else:
                logger.error(f"Failed to send error notification: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending error notification: {e}")
            return False