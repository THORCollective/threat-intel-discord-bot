import discord
import asyncio
import logging
from typing import Optional
from src.config import DISCORD_BOT_TOKEN, DISCORD_CHANNEL_ID, DRY_RUN

logger = logging.getLogger(__name__)


class DiscordPoster:
    def __init__(self):
        """Initialize Discord bot client."""
        self.bot_token = DISCORD_BOT_TOKEN
        self.channel_id = DISCORD_CHANNEL_ID
        
        if not self.bot_token:
            logger.warning("Discord bot token not configured")
            self.client = None
        else:
            # Configure intents for the bot
            intents = discord.Intents.default()
            intents.message_content = True
            self.client = discord.Client(intents=intents)
            logger.info("Discord client initialized")
    
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
        Send formatted message to Discord using bot API.
        
        Args:
            analysis: AI analysis text
            title: Article title
            url: Article URL
            
        Returns:
            True if posted successfully, False otherwise
        """
        if not self.client or DRY_RUN:
            logger.info(f"Skipping Discord post (dry_run={DRY_RUN}, client={bool(self.client)})")
            if DRY_RUN:
                message = self.format_discord_message(analysis, title, url)
                logger.info(f"[DRY RUN] Would post to Discord:\n{message[:500]}...")
            return True
        
        # Format message
        message = self.format_discord_message(analysis, title, url)
        
        # Run the async posting function
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self._post_message_async(message))
            loop.close()
            return result
        except Exception as e:
            logger.error(f"Error running async Discord post: {e}")
            return False
    
    async def _post_message_async(self, message: str) -> bool:
        """
        Async function to post message to Discord.
        
        Args:
            message: Formatted message to post
            
        Returns:
            True if posted successfully, False otherwise
        """
        try:
            # Get the channel ID
            if not self.channel_id:
                logger.error("Discord channel ID not configured")
                return False
                
            try:
                channel_id_int = int(self.channel_id)
            except ValueError:
                logger.error(f"Invalid channel ID format: {self.channel_id}")
                return False
            
            # Create event for when bot is ready
            ready_event = asyncio.Event()
            message_sent = False
            
            @self.client.event
            async def on_ready():
                nonlocal message_sent
                logger.info(f"Bot connected as: {self.client.user}")
                
                # Get the channel
                channel = self.client.get_channel(channel_id_int)
                if not channel:
                    logger.error(f"Could not find channel with ID: {self.channel_id}")
                    # List available channels for debugging
                    logger.info("Available channels:")
                    for guild in self.client.guilds:
                        for ch in guild.text_channels:
                            logger.info(f"  - {ch.name} (ID: {ch.id})")
                else:
                    logger.info(f"Found channel: {channel.name} in {channel.guild.name}")
                    await channel.send(message)
                    logger.info("Successfully posted to Discord")
                    message_sent = True
                
                ready_event.set()
                await self.client.close()
            
            # Start the client
            logger.info("Connecting to Discord...")
            await self.client.start(self.bot_token)
            
            # Wait for ready event
            await ready_event.wait()
            return message_sent
            
        except discord.LoginFailure:
            logger.error("Discord login failed - check bot token")
            return False
        except discord.Forbidden:
            logger.error("Bot doesn't have permission to send messages in this channel")
            return False
        except discord.HTTPException as e:
            logger.error(f"Discord HTTP error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error posting to Discord: {e}")
            return False
        finally:
            if not self.client.is_closed():
                await self.client.close()
    
    def send_error_notification(self, error_msg: str) -> bool:
        """
        Send error notification to Discord using bot API.
        
        Args:
            error_msg: Error message to send
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.client or DRY_RUN:
            logger.info(f"Skipping error notification (dry_run={DRY_RUN}, client={bool(self.client)})")
            return True
        
        error_message = f"⚠️ **Threat Intel Bot Error** ⚠️\n\n{error_msg}"
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self._post_message_async(error_message))
            loop.close()
            return result
        except Exception as e:
            logger.error(f"Error sending error notification: {e}")
            return False