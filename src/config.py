import os
from typing import List, Dict

# RSS feed sources configuration
RSS_SOURCES: List[Dict[str, str]] = [
    {"name": "DFIR", "url": "https://thedfirreport.com/feed/"},
    {"name": "CISA", "url": "https://www.cisa.gov/cybersecurity-advisories/all.xml"},
    {"name": "Sophos Threat Research", "url": "https://news.sophos.com/en-us/category/threat-research/feed/"},
    {"name": "Sophos SecOps", "url": "https://news.sophos.com/en-us/category/security-operations/feed/"},
    {"name": "TheHackerNews", "url": "https://feeds.feedburner.com/TheHackersNews?format=xml"}
]

# OpenAI prompt template
OPENAI_PROMPT = """You're an advanced threat hunter writing for other seasoned threat hunters.

Based on the following threat report, extract the most valuable insights and structure your response using the PEAK Threat Hunting Framework – formatted for quick Discord delivery.

Respond in this structure, using tight bullet points and clean formatting:

**TTPs:** List relevant MITRE ATT&CK technique IDs (e.g., T1059.001, T1021.002)

**Prepare**
- Describe the threat, tradecraft, or behavior
- Focus on what makes it interesting or non-obvious

**Execute**
- List key log sources to investigate
- Provide 1–2 example Splunk SPL queries that hunt for this behavior

**Act w/ Knowledge**
- Offer a durable insight or follow-up hunt idea
- This can include clustering, baselining, or visibility improvements

Stay under 1200 characters. Be precise, helpful, and sharp – no summaries or fluff.

---

{article_content}"""

# HTTP headers for web scraping
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Content extraction settings
CONTENT_SELECTOR = ".entry-content"
MAX_CONTENT_LENGTH = 10000

# Retry settings
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# Environment variables
NOTION_API_TOKEN = os.environ.get("NOTION_API_TOKEN")
NOTION_DATABASE_ID = os.environ.get("NOTION_DATABASE_ID", "1e7f1554-e9cf-8020-bce6-eb3bc8cc5828")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
DRY_RUN = os.environ.get("DRY_RUN", "false").lower() == "true"

# OpenAI configuration
OPENAI_MODEL = "gpt-3.5-turbo"
OPENAI_MAX_TOKENS = 1500
OPENAI_TEMPERATURE = 0.7

# Logging configuration
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"