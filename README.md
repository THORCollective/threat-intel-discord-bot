# Threat Intel Discord Bot

A GitHub Actions-powered bot that automatically fetches, analyzes, and shares threat intelligence reports daily to Discord using the PEAK Threat Hunting Framework.

## Features

- 🔄 **Daily Automated Runs**: Executes at 10 AM UTC via GitHub Actions
- 📰 **RSS Feed Rotation**: Cycles through multiple threat intelligence sources
- 🔍 **Duplicate Detection**: Checks Notion database to avoid reposting content
- 🤖 **AI-Powered Analysis**: Uses OpenAI GPT-3.5 to generate PEAK Framework analysis
- 💬 **Discord Integration**: Posts formatted threat intelligence to Discord channel
- 📝 **Notion Storage**: Saves all processed articles and analyses to Notion database
- 🛡️ **Error Handling**: Comprehensive error handling with Discord notifications

## RSS Sources

The bot rotates daily through these threat intelligence sources:
- DFIR Report
- CISA Cybersecurity Advisories
- Sophos Threat Research
- Sophos Security Operations
- TheHackerNews

## PEAK Framework Analysis

Each threat report is analyzed using the PEAK Threat Hunting Framework:

- **TTPs**: MITRE ATT&CK technique IDs
- **Prepare**: Threat description and interesting behaviors
- **Execute**: Log sources and example Splunk queries
- **Act w/ Knowledge**: Follow-up hunt ideas and insights

## Setup

### Prerequisites

- GitHub repository with Actions enabled
- Notion integration and database
- OpenAI API key
- Discord webhook URL

### GitHub Secrets Configuration

Add these secrets to your GitHub repository:

1. **NOTION_API_TOKEN**: Your Notion integration token
   - Create at: https://www.notion.so/my-integrations
   - Grant access to your database

2. **NOTION_DATABASE_ID**: Your Notion database ID
   - Default: `1e7f1554-e9cf-8020-bce6-eb3bc8cc5828`
   - Find in your database URL

3. **OPENAI_API_KEY**: Your OpenAI API key
   - Get from: https://platform.openai.com/api-keys

4. **DISCORD_BOT_TOKEN**: Your Discord bot token
   - Create bot at: https://discord.com/developers/applications
   - Generate token in Bot section

5. **DISCORD_CHANNEL_ID**: Your Discord channel ID (optional)
   - Right-click channel → Copy Channel ID
   - Default: 1332616096825606164

### Notion Database Setup

Create a Notion database with these properties:
- **Title** (title): Article title
- **Snippet** (text): Content preview
- **Author** (text): Article creator
- **Source Link** (url): Article URL
- **Date** (date): Publication date

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/threat-intel-discord-bot.git
cd threat-intel-discord-bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set environment variables:
```bash
export NOTION_API_TOKEN="your_token"
export NOTION_DATABASE_ID="your_database_id"
export OPENAI_API_KEY="your_api_key"
export DISCORD_BOT_TOKEN="your_bot_token"
export DISCORD_CHANNEL_ID="1332616096825606164"
```

4. Run in dry-run mode:
```bash
DRY_RUN=true python -m src.main
```

## Usage

### Automatic Daily Runs

The bot runs automatically every day at 10 AM UTC via GitHub Actions.

### Manual Trigger

You can manually trigger the workflow:
1. Go to Actions tab in your GitHub repository
2. Select "Daily Threat Hunt" workflow
3. Click "Run workflow"
4. Optionally enable dry-run mode

### Dry Run Mode

Test the bot without posting to Discord or Notion:
- Via GitHub Actions: Select "true" for dry_run input
- Locally: Set `DRY_RUN=true` environment variable

## Project Structure

```
threat-intel-discord-bot/
├── .github/
│   └── workflows/
│       └── daily-threat-hunt.yml      # GitHub Actions workflow
├── src/
│   ├── main.py                        # Main orchestrator
│   ├── config.py                      # Configuration
│   ├── rss_handler.py                 # RSS feed processing
│   ├── notion_client.py               # Notion operations
│   ├── content_processor.py           # Web scraping
│   ├── ai_analyzer.py                 # OpenAI integration
│   └── discord_poster.py              # Discord posting
├── requirements.txt                   # Dependencies
├── .gitignore                         # Git ignore rules
└── README.md                          # Documentation
```

## Error Handling

The bot includes comprehensive error handling:
- Retries for network requests (3 attempts)
- Discord notifications for critical failures
- Detailed logging to file and console
- Graceful degradation when services unavailable

## Monitoring

- **GitHub Actions**: Check workflow runs in Actions tab
- **Logs**: Download artifacts from failed runs
- **Discord**: Receive error notifications
- **Notion**: Track processed articles

## Customization

### Modify RSS Sources

Edit `RSS_SOURCES` in `src/config.py`:
```python
RSS_SOURCES = [
    {"name": "Source Name", "url": "https://example.com/feed"},
    # Add more sources...
]
```

### Adjust AI Prompt

Modify `OPENAI_PROMPT` in `src/config.py` to change analysis format.

### Change Schedule

Edit cron expression in `.github/workflows/daily-threat-hunt.yml`:
```yaml
schedule:
  - cron: '0 10 * * *'  # Daily at 10 AM UTC
```

## Troubleshooting

### Bot Not Running
- Check GitHub Actions is enabled
- Verify all secrets are configured
- Review workflow logs for errors

### Notion Errors
- Verify integration has database access
- Check database ID is correct
- Ensure property names match

### Discord Not Posting
- Verify bot token is valid and bot is in server
- Check bot has permission to send messages in target channel
- Ensure channel ID is correct
- Review Discord rate limits

### OpenAI Errors
- Check API key is valid
- Verify account has credits
- Review usage limits

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review logs for detailed error information