import feedparser
import logging
from datetime import datetime
from typing import Dict, Optional
from src.config import RSS_SOURCES

logger = logging.getLogger(__name__)


def get_daily_source() -> Dict[str, str]:
    """
    Returns RSS source based on current date.
    Rotates through sources daily.
    """
    day_of_year = datetime.now().timetuple().tm_yday
    source_index = (day_of_year - 1) % len(RSS_SOURCES)
    source = RSS_SOURCES[source_index]
    
    logger.info(f"Selected daily RSS source: {source['name']}")
    return source


def fetch_rss_feed(url: str) -> Optional[feedparser.FeedParserDict]:
    """
    Parse RSS feed from given URL.
    
    Args:
        url: RSS feed URL
        
    Returns:
        Parsed feed object or None if error
    """
    try:
        logger.info(f"Fetching RSS feed from: {url}")
        feed = feedparser.parse(url)
        
        if feed.bozo:
            logger.warning(f"Feed parsing had issues but continuing: {feed.bozo_exception}")
        
        if not feed.entries:
            logger.error(f"No entries found in RSS feed: {url}")
            return None
            
        logger.info(f"Successfully fetched {len(feed.entries)} entries from RSS feed")
        return feed
        
    except Exception as e:
        logger.error(f"Error fetching RSS feed: {e}")
        return None


def get_latest_article(feed: feedparser.FeedParserDict) -> Optional[Dict[str, str]]:
    """
    Extract latest article from RSS feed.
    
    Args:
        feed: Parsed RSS feed
        
    Returns:
        Article data dictionary or None if no entries
    """
    if not feed or not feed.entries:
        logger.error("No entries in feed")
        return None
    
    # Get the first (latest) entry
    latest_entry = feed.entries[0]
    
    logger.info(f"Found latest article: {latest_entry.get('title', 'No title')}")
    return extract_article_data(latest_entry)


def extract_article_data(entry: Dict) -> Dict[str, str]:
    """
    Standardize article data format from RSS entry.
    
    Args:
        entry: RSS feed entry
        
    Returns:
        Standardized article data dictionary
    """
    # Extract content snippet
    content_snippet = ""
    if hasattr(entry, 'summary'):
        content_snippet = entry.summary
    elif hasattr(entry, 'description'):
        content_snippet = entry.description
    elif hasattr(entry, 'content') and entry.content:
        content_snippet = entry.content[0].get('value', '')
    
    # Clean HTML from snippet if present
    import re
    content_snippet = re.sub(r'<[^>]+>', '', content_snippet)
    content_snippet = content_snippet[:500]  # Limit snippet length
    
    # Extract creator/author
    creator = "Unknown"
    if hasattr(entry, 'author'):
        creator = entry.author
    elif hasattr(entry, 'dc_creator'):
        creator = entry.dc_creator
    elif hasattr(entry, 'authors') and entry.authors:
        creator = entry.authors[0].get('name', 'Unknown')
    
    # Extract publication date
    pub_date = ""
    if hasattr(entry, 'published'):
        pub_date = entry.published
    elif hasattr(entry, 'updated'):
        pub_date = entry.updated
    elif hasattr(entry, 'created'):
        pub_date = entry.created
    
    # Parse date to standard format if available
    if pub_date:
        try:
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(pub_date)
            pub_date = dt.strftime("%Y-%m-%d")
        except:
            pub_date = datetime.now().strftime("%Y-%m-%d")
    else:
        pub_date = datetime.now().strftime("%Y-%m-%d")
    
    article_data = {
        "title": entry.get('title', 'No Title'),
        "link": entry.get('link', ''),
        "content_snippet": content_snippet,
        "creator": creator,
        "pub_date": pub_date
    }
    
    logger.info(f"Extracted article data: {article_data['title']}")
    return article_data