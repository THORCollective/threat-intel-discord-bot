#!/usr/bin/env python3
import logging
import sys
from typing import Optional, Dict
from src.config import LOG_FORMAT, LOG_LEVEL, DRY_RUN
from src.rss_handler import get_daily_source, fetch_rss_feed, get_latest_article, get_sources_in_priority_order
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
    Loops through RSS sources until finding non-duplicate content.
    
    Returns:
        True if successful, False otherwise
    """
    logger.info("=" * 50)
    logger.info("Starting Threat Intel Bot")
    logger.info(f"Dry run mode: {DRY_RUN}")
    logger.info("=" * 50)
    
    # Initialize Notion client once
    notion = NotionHandler()
    
    # Try RSS sources starting with daily source, then others
    sources_to_try = get_sources_in_priority_order()
    tried_sources = []
    
    for source_index, source in enumerate(sources_to_try):
        try:
            logger.info(f"Trying RSS source {source_index + 1}/{len(sources_to_try)}: {source['name']}")
            tried_sources.append(source['name'])
            
            # Step 1: Fetch RSS feed
            logger.info(f"Fetching RSS feed from {source['name']}")
            feed = fetch_rss_feed(source['url'])
            if not feed:
                logger.warning(f"Failed to fetch RSS feed from {source['name']}, trying next source")
                continue
            
            # Step 2: Get latest article
            logger.info("Extracting latest article")
            article_data = get_latest_article(feed)
            if not article_data:
                logger.warning(f"No articles found in {source['name']} RSS feed, trying next source")
                continue
            
            logger.info(f"Found article: {article_data['title']}")
            logger.info(f"Article URL: {article_data['link']}")
            
            # Step 3: Check for duplicate in Notion
            logger.info("Checking for duplicate in Notion")
            if notion.client:
                is_duplicate = notion.check_duplicate_url(article_data['link'])
                if is_duplicate:
                    logger.info(f"Article from {source['name']} already exists in Notion database")
                    # Continue to next source instead of skipping
                    continue
            else:
                logger.warning("Notion client not initialized, skipping duplicate check")
            
            # Found a non-duplicate article, process it
            logger.info(f"Processing new article from {source['name']}")
            
            # Step 4: Process article content
            logger.info("Processing article content")
            article_content = process_article_url(article_data['link'])
            if not article_content:
                logger.warning("Failed to extract article content, using snippet")
                article_content = article_data['content_snippet']
            
            # Step 5: AI Analysis
            logger.info("Performing AI analysis")
            ai_analyzer = AIAnalyzer()
            ai_analysis = ai_analyzer.process_article(article_content)
            
            if not ai_analysis:
                logger.warning("AI analysis failed, using fallback message")
                ai_analysis = "Unable to generate AI analysis for this article. Please review the full article for threat intelligence insights."
            
            # Step 6: Post to Discord
            logger.info("Posting to Discord")
            discord = DiscordPoster()
            discord_success = discord.post_to_discord(
                analysis=ai_analysis,
                title=article_data['title'],
                url=article_data['link']
            )
            
            if not discord_success:
                logger.error("Failed to post to Discord")
            
            # Step 7: Save to Notion
            logger.info("Saving to Notion")
            article_data['ai_analysis'] = ai_analysis
            notion_success = notion.save_article_to_notion(article_data)
            
            if not notion_success:
                logger.error("Failed to save to Notion")
            
            # Success! We found and processed a new article
            logger.info("=" * 50)
            logger.info("Threat Intel Bot completed successfully")
            logger.info(f"Source used: {source['name']}")
            logger.info(f"Processed article: {article_data['title']}")
            logger.info(f"Discord posted: {discord_success}")
            logger.info(f"Notion saved: {notion_success}")
            logger.info(f"Sources tried: {', '.join(tried_sources)}")
            logger.info("=" * 50)
            
            return discord_success and notion_success
            
        except Exception as e:
            logger.error(f"Error processing {source['name']}: {e}")
            continue  # Try next source
    
    # If we get here, we've tried all sources and found only duplicates or errors
    logger.info("=" * 50)
    logger.info("All RSS sources checked - no new content found")
    logger.info(f"Sources tried: {', '.join(tried_sources)}")
    logger.info("Skipping for today - all latest articles already exist in Notion database")
    logger.info("=" * 50)
    return True  # Not an error, just no new content


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