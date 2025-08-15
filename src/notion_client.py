import logging
from typing import Dict, Optional
from notion_client import Client
from src.config import NOTION_API_TOKEN, NOTION_DATABASE_ID, DRY_RUN

logger = logging.getLogger(__name__)


class NotionHandler:
    def __init__(self):
        """Initialize Notion client."""
        if not NOTION_API_TOKEN:
            logger.warning("Notion API token not configured")
            self.client = None
        else:
            self.client = Client(auth=NOTION_API_TOKEN)
            logger.info("Notion client initialized")
    
    def check_duplicate_url(self, url: str) -> bool:
        """
        Query database for existing URL.
        
        Args:
            url: Article URL to check
            
        Returns:
            True if URL exists, False otherwise
        """
        if not self.client or DRY_RUN:
            logger.info(f"Skipping duplicate check (dry_run={DRY_RUN}, client={bool(self.client)})")
            return False
        
        try:
            logger.info(f"Checking for duplicate URL in Notion: {url}")
            
            # Query the database with filter
            response = self.client.databases.query(
                database_id=NOTION_DATABASE_ID,
                filter={
                    "property": "Source Link",
                    "url": {
                        "equals": url
                    }
                }
            )
            
            # Check if any results found
            is_duplicate = len(response.get("results", [])) > 0
            
            if is_duplicate:
                logger.info(f"URL already exists in Notion database: {url}")
            else:
                logger.info(f"URL is new, not found in Notion database")
                
            return is_duplicate
            
        except Exception as e:
            logger.error(f"Error checking for duplicate URL: {e}")
            # On error, assume not duplicate to allow processing
            return False
    
    def save_article_to_notion(self, article_data: Dict) -> bool:
        """
        Save article metadata to Notion database.
        
        Args:
            article_data: Article data dictionary with analysis
            
        Returns:
            True if saved successfully, False otherwise
        """
        if not self.client or DRY_RUN:
            logger.info(f"Skipping Notion save (dry_run={DRY_RUN}, client={bool(self.client)})")
            return True
        
        try:
            logger.info(f"Saving article to Notion: {article_data.get('title', 'No title')}")
            
            # Prepare page properties
            properties = {
                "Title": {
                    "title": [
                        {
                            "text": {
                                "content": article_data.get("title", "No Title")[:100]
                            }
                        }
                    ]
                },
                "Snippet": {
                    "rich_text": [
                        {
                            "text": {
                                "content": article_data.get("content_snippet", "")[:2000]
                            }
                        }
                    ]
                },
                "Author": {
                    "rich_text": [
                        {
                            "text": {
                                "content": article_data.get("creator", "Unknown")[:100]
                            }
                        }
                    ]
                },
                "Source Link": {
                    "url": article_data.get("link", "")
                }
            }
            
            # Add date if available
            if article_data.get("pub_date"):
                properties["Date"] = {
                    "date": {
                        "start": article_data["pub_date"]
                    }
                }
            
            # Create the page
            response = self.client.pages.create(
                parent={"database_id": NOTION_DATABASE_ID},
                properties=properties,
                children=[
                    {
                        "object": "block",
                        "type": "heading_2",
                        "heading_2": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": "AI Analysis"
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": article_data.get("ai_analysis", "No analysis available")[:2000]
                                    }
                                }
                            ]
                        }
                    }
                ]
            )
            
            logger.info(f"Successfully saved article to Notion: {response.get('id')}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving article to Notion: {e}")
            return False
    
    def test_connection(self) -> bool:
        """
        Test Notion API connection and database access.
        
        Returns:
            True if connection successful, False otherwise
        """
        if not self.client:
            logger.error("Notion client not initialized")
            return False
        
        try:
            # Try to retrieve database
            response = self.client.databases.retrieve(database_id=NOTION_DATABASE_ID)
            logger.info(f"Successfully connected to Notion database: {response.get('title', [{}])[0].get('plain_text', 'Untitled')}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Notion database: {e}")
            return False