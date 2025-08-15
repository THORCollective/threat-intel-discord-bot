#!/usr/bin/env python3
import logging
import sys
from typing import Optional, Dict
from src.config import LOG_FORMAT, LOG_LEVEL, DRY_RUN
from src.rss_handler import get_daily_source, fetch_rss_feed, get_latest_article
from src.notion_client import NotionHandler
from src.content_processor import process_article_url
from src.ai_analyzer import AIAnalyzer
from src.discord_poster import DiscordPoster

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('threat_intel_bot.log')
    ]
)

logger = logging.getLogger(__name__)


def handle_error(error: Exception, context: str) -> None:
    """
    Handle errors with logging and Discord notification.
    
    Args:
        error: The exception that occurred
        context: Context about where the error occurred
    """
    error_msg = f"Error in {context}: {str(error)}"
    logger.error(error_msg, exc_info=True)
    
    # Send Discord notification for critical errors
    try:
        discord = DiscordPoster()
        discord.send_error_notification(error_msg)
    except Exception as e:
        logger.error(f"Failed to send error notification: {e}")


def process_threat_intel() -> bool:
    """
    Main processing function for threat intelligence workflow.
    
    Returns:
        True if successful, False otherwise
    """
    logger.info("=" * 50)
    logger.info("Starting Threat Intel Bot")
    logger.info(f"Dry run mode: {DRY_RUN}")
    logger.info("=" * 50)
    
    try:
        # Step 1: Get daily RSS source
        logger.info("Step 1: Getting daily RSS source")
        daily_source = get_daily_source()
        
        # Step 2: Fetch RSS feed
        logger.info(f"Step 2: Fetching RSS feed from {daily_source['name']}")
        feed = fetch_rss_feed(daily_source['url'])
        if not feed:
            raise Exception(f"Failed to fetch RSS feed from {daily_source['name']}")
        
        # Step 3: Get latest article
        logger.info("Step 3: Extracting latest article")
        article_data = get_latest_article(feed)
        if not article_data:
            raise Exception("No articles found in RSS feed")
        
        logger.info(f"Latest article: {article_data['title']}")
        logger.info(f"Article URL: {article_data['link']}")
        
        # Step 4: Check for duplicate in Notion
        logger.info("Step 4: Checking for duplicate in Notion")
        notion = NotionHandler()
        
        if notion.client:
            is_duplicate = notion.check_duplicate_url(article_data['link'])
            if is_duplicate:
                logger.info("Article already exists in Notion database, skipping")
                return True
        else:
            logger.warning("Notion client not initialized, skipping duplicate check")
        
        # Step 5: Process article content
        logger.info("Step 5: Processing article content")
        article_content = process_article_url(article_data['link'])
        if not article_content:
            logger.warning("Failed to extract article content, using snippet")
            article_content = article_data['content_snippet']
        
        # Step 6: AI Analysis
        logger.info("Step 6: Performing AI analysis")
        ai_analyzer = AIAnalyzer()
        ai_analysis = ai_analyzer.process_article(article_content)
        
        if not ai_analysis:
            logger.warning("AI analysis failed, using fallback message")
            ai_analysis = "Unable to generate AI analysis for this article. Please review the full article for threat intelligence insights."
        
        # Step 7: Post to Discord
        logger.info("Step 7: Posting to Discord")
        discord = DiscordPoster()
        discord_success = discord.post_to_discord(
            analysis=ai_analysis,
            title=article_data['title'],
            url=article_data['link']
        )
        
        if not discord_success:
            logger.error("Failed to post to Discord")
        
        # Step 8: Save to Notion
        logger.info("Step 8: Saving to Notion")
        article_data['ai_analysis'] = ai_analysis
        notion_success = notion.save_article_to_notion(article_data)
        
        if not notion_success:
            logger.error("Failed to save to Notion")
        
        # Summary
        logger.info("=" * 50)
        logger.info("Threat Intel Bot completed successfully")
        logger.info(f"Processed article: {article_data['title']}")
        logger.info(f"Discord posted: {discord_success}")
        logger.info(f"Notion saved: {notion_success}")
        logger.info("=" * 50)
        
        return discord_success and notion_success
        
    except Exception as e:
        handle_error(e, "main processing")
        return False


def main() -> None:
    """
    Main entry point for the threat intel bot.
    """
    try:
        # Test connections if in dry run mode
        if DRY_RUN:
            logger.info("Running in DRY RUN mode - no actual posts will be made")
            
            # Test Notion connection
            notion = NotionHandler()
            if notion.client:
                notion.test_connection()
            
            # Test OpenAI connection (just check if key exists)
            ai = AIAnalyzer()
            if ai.client:
                logger.info("OpenAI client initialized successfully")
            
            # Test Discord webhook (just check if URL exists)
            discord = DiscordPoster()
            if discord.webhook_url:
                logger.info("Discord webhook URL configured")
        
        # Run main processing
        success = process_threat_intel()
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        logger.info("Bot interrupted by user")
        sys.exit(0)
    except Exception as e:
        handle_error(e, "main")
        sys.exit(1)


if __name__ == "__main__":
    main()