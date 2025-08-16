#!/usr/bin/env python3
"""
Test the Discord bot locally with a sample message
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Import our Discord poster
from src.discord_poster import DiscordPoster

def test_discord_post():
    """Test Discord posting with a sample threat intel message."""
    
    print("🤖 Testing Discord Bot Posting")
    print("=" * 40)
    
    # Create Discord poster
    poster = DiscordPoster()
    
    # Sample threat intel message
    test_analysis = """**TTPs:** T1566.001, T1059.001, T1055

**Prepare**
• New ransomware variant leveraging living-off-the-land techniques
• Uses legitimate Windows tools to evade detection

**Execute**
• Check Windows Event Logs (4688, 7045)
• `index=windows EventCode=4688 | stats count by CommandLine`

**Act w/ Knowledge**
• Baseline PowerShell usage patterns in your environment
• Monitor for unusual parent-child process relationships"""
    
    # Post the message
    success = poster.post_to_discord(
        analysis=test_analysis,
        title="TEST: Discord Bot Connection",
        url="https://github.com/THORCollective/threat-intel-discord-bot"
    )
    
    if success:
        print("✅ Successfully posted test message to Discord!")
    else:
        print("❌ Failed to post to Discord - check logs above")
    
    return success

if __name__ == "__main__":
    # Make sure token is set
    if not os.environ.get("DISCORD_BOT_TOKEN"):
        print("❌ Please set DISCORD_BOT_TOKEN environment variable")
        sys.exit(1)
    
    success = test_discord_post()
    sys.exit(0 if success else 1)