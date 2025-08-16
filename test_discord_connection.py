#!/usr/bin/env python3
"""
Discord Bot Connection Test
Run this to troubleshoot Discord bot connectivity issues.
"""

import discord
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DISCORD_BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
DISCORD_CHANNEL_ID = os.environ.get("DISCORD_CHANNEL_ID", "1332616096825606164")

async def test_discord_connection():
    """Test Discord bot connection and channel access."""
    
    print("🤖 Discord Bot Connection Test")
    print("=" * 40)
    
    if not DISCORD_BOT_TOKEN:
        print("❌ DISCORD_BOT_TOKEN not found in environment variables")
        print("   Set it with: export DISCORD_BOT_TOKEN='your_token_here'")
        return
    
    print(f"✅ Bot token configured (ending in: ...{DISCORD_BOT_TOKEN[-10:]})")
    print(f"🎯 Target channel ID: {DISCORD_CHANNEL_ID}")
    print()
    
    # Configure intents
    intents = discord.Intents.default()
    intents.message_content = True
    
    client = discord.Client(intents=intents)
    
    @client.event
    async def on_ready():
        print(f"✅ Bot logged in as: {client.user}")
        print(f"🏠 Bot is in {len(client.guilds)} server(s):")
        
        for guild in client.guilds:
            print(f"   - {guild.name} (ID: {guild.id})")
        
        print()
        
        # Try to find the channel
        channel = client.get_channel(int(DISCORD_CHANNEL_ID))
        
        if channel:
            print(f"✅ Found channel: #{channel.name} in {channel.guild.name}")
            print(f"📊 Channel type: {type(channel).__name__}")
            
            # Check permissions
            permissions = channel.permissions_for(channel.guild.me)
            print("🔐 Bot permissions in this channel:")
            print(f"   - View Channel: {permissions.view_channel}")
            print(f"   - Send Messages: {permissions.send_messages}")
            print(f"   - Read Message History: {permissions.read_message_history}")
            
            if permissions.send_messages:
                try:
                    # Send a test message
                    await channel.send("🧪 **Discord Bot Test** - Connection successful! This message confirms the bot can post to this channel.")
                    print("✅ Test message sent successfully!")
                except Exception as e:
                    print(f"❌ Failed to send test message: {e}")
            else:
                print("❌ Bot doesn't have permission to send messages")
                
        else:
            print(f"❌ Could not find channel with ID: {DISCORD_CHANNEL_ID}")
            print("\n🔍 Available channels the bot can see:")
            
            for guild in client.guilds:
                print(f"\n📁 {guild.name}:")
                for channel in guild.text_channels:
                    print(f"   - #{channel.name} (ID: {channel.id})")
        
        await client.close()
    
    @client.event
    async def on_error(event, *args, **kwargs):
        print(f"❌ Discord error in {event}: {args}")
    
    try:
        print("🔌 Connecting to Discord...")
        await client.start(DISCORD_BOT_TOKEN)
    except discord.LoginFailure:
        print("❌ Login failed - invalid bot token")
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    asyncio.run(test_discord_connection())