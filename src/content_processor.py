import requests
import logging
import time
from bs4 import BeautifulSoup
from typing import Optional
from src.config import USER_AGENT, CONTENT_SELECTOR, MAX_CONTENT_LENGTH, MAX_RETRIES, RETRY_DELAY

logger = logging.getLogger(__name__)


def fetch_full_article(url: str) -> Optional[str]:
    """
    HTTP request with headers to fetch full article content.
    
    Args:
        url: Article URL
        
    Returns:
        HTML content or None if error
    """
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    for attempt in range(MAX_RETRIES):
        try:
            logger.info(f"Fetching article content from: {url} (attempt {attempt + 1}/{MAX_RETRIES})")
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            logger.info(f"Successfully fetched article content, status code: {response.status_code}")
            return response.text
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
            else:
                logger.error(f"Failed to fetch article after {MAX_RETRIES} attempts: {e}")
                return None
    
    return None


def extract_content(html: str) -> Optional[str]:
    """
    BeautifulSoup extraction of article content.
    
    Args:
        html: HTML content
        
    Returns:
        Extracted text content or None if error
    """
    try:
        logger.info("Extracting content from HTML")
        soup = BeautifulSoup(html, 'lxml')
        
        # Try primary content selector
        content = soup.select_one(CONTENT_SELECTOR)
        
        # Fallback selectors if primary fails
        if not content:
            logger.info("Primary selector failed, trying fallback selectors")
            fallback_selectors = [
                ".l-content",  # CISA specific
                ".node-content",  # CISA specific
                ".field-name-body",  # CISA specific
                "article",
                "main",
                "[role='main']",
                ".post-content",
                ".article-content",
                ".content",
                "#content",
                "div.entry",
                "div.post"
            ]
            
            for selector in fallback_selectors:
                content = soup.select_one(selector)
                if content:
                    logger.info(f"Content found with selector: {selector}")
                    break
        
        # If still no content, try to get body
        if not content:
            logger.warning("No content selector worked, using body as fallback")
            content = soup.body
        
        if not content:
            logger.error("No content could be extracted")
            return None
        
        # Extract text
        text = content.get_text(separator='\n', strip=True)
        
        logger.info(f"Extracted {len(text)} characters of content")
        return text
        
    except Exception as e:
        logger.error(f"Error extracting content: {e}")
        return None


def clean_article_text(content: str) -> str:
    """
    Clean up extracted text content.
    
    Args:
        content: Raw extracted text
        
    Returns:
        Cleaned text
    """
    if not content:
        return ""
    
    logger.info("Cleaning article text")
    
    # Remove common footer/subscription prompts
    remove_patterns = [
        "Subscribe to our newsletter",
        "Sign up for our",
        "Get our free",
        "Join our mailing",
        "Follow us on",
        "Share this article",
        "Related articles",
        "You might also like",
        "Advertisement",
        "Sponsored content",
        "Cookie policy",
        "Privacy policy",
        "Terms of service"
    ]
    
    lines = content.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Skip lines with unwanted patterns
        skip_line = False
        for pattern in remove_patterns:
            if pattern.lower() in line.lower():
                skip_line = True
                break
        
        if not skip_line and line.strip():
            cleaned_lines.append(line.strip())
    
    # Join lines and remove excessive newlines
    cleaned_text = '\n'.join(cleaned_lines)
    
    # Replace multiple newlines with double newlines
    import re
    cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
    
    # Trim to max length
    if len(cleaned_text) > MAX_CONTENT_LENGTH:
        logger.info(f"Trimming content from {len(cleaned_text)} to {MAX_CONTENT_LENGTH} characters")
        cleaned_text = cleaned_text[:MAX_CONTENT_LENGTH] + "..."
    
    logger.info(f"Cleaned text to {len(cleaned_text)} characters")
    return cleaned_text


def process_article_url(url: str) -> Optional[str]:
    """
    Complete article processing pipeline.
    
    Args:
        url: Article URL
        
    Returns:
        Cleaned article text or None if error
    """
    logger.info(f"Starting article processing for: {url}")
    
    # Fetch HTML
    html = fetch_full_article(url)
    if not html:
        return None
    
    # Extract content
    content = extract_content(html)
    if not content:
        return None
    
    # Clean text
    cleaned = clean_article_text(content)
    
    logger.info(f"Article processing complete, final length: {len(cleaned)} characters")
    return cleaned