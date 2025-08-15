import logging
from typing import Optional
from openai import OpenAI
from src.config import (
    OPENAI_API_KEY, 
    OPENAI_PROMPT, 
    OPENAI_MODEL,
    OPENAI_MAX_TOKENS,
    OPENAI_TEMPERATURE,
    DRY_RUN
)

logger = logging.getLogger(__name__)


class AIAnalyzer:
    def __init__(self):
        """Initialize OpenAI client."""
        if not OPENAI_API_KEY:
            logger.warning("OpenAI API key not configured")
            self.client = None
        else:
            self.client = OpenAI(api_key=OPENAI_API_KEY)
            logger.info("OpenAI client initialized")
    
    def analyze_with_openai(self, content: str) -> Optional[str]:
        """
        Send content to GPT-3.5-turbo for analysis.
        
        Args:
            content: Article content to analyze
            
        Returns:
            AI analysis response or None if error
        """
        if not self.client or DRY_RUN:
            logger.info(f"Skipping AI analysis (dry_run={DRY_RUN}, client={bool(self.client)})")
            if DRY_RUN:
                return "**[DRY RUN MODE]** AI analysis would be performed here with the PEAK Threat Hunting Framework."
            return None
        
        try:
            logger.info("Sending content to OpenAI for analysis")
            
            # Prepare the prompt with article content
            prompt = OPENAI_PROMPT.format(article_content=content)
            
            # Make API call
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert threat hunter specializing in actionable threat intelligence analysis."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=OPENAI_MAX_TOKENS,
                temperature=OPENAI_TEMPERATURE
            )
            
            # Extract response
            analysis = response.choices[0].message.content
            
            logger.info(f"Received AI analysis, length: {len(analysis)} characters")
            return analysis
            
        except Exception as e:
            logger.error(f"Error during OpenAI analysis: {e}")
            return None
    
    def format_response(self, ai_response: str) -> str:
        """
        Clean up and format AI response for Discord.
        
        Args:
            ai_response: Raw AI response
            
        Returns:
            Formatted response
        """
        if not ai_response:
            return "Analysis unavailable."
        
        logger.info("Formatting AI response")
        
        # Trim to Discord character limit (considering the rest of the message)
        # Discord has a 2000 char limit, leave room for header/footer
        max_analysis_length = 1200
        
        if len(ai_response) > max_analysis_length:
            logger.info(f"Trimming AI response from {len(ai_response)} to {max_analysis_length} characters")
            # Try to cut at a sentence boundary
            ai_response = ai_response[:max_analysis_length]
            last_period = ai_response.rfind('.')
            last_newline = ai_response.rfind('\n')
            cut_point = max(last_period, last_newline)
            
            if cut_point > max_analysis_length - 200:  # If we found a good cut point
                ai_response = ai_response[:cut_point + 1]
            else:
                ai_response = ai_response.strip() + "..."
        
        # Ensure proper Discord formatting
        # Fix any broken markdown
        import re
        
        # Count asterisks to ensure they're balanced
        asterisk_count = ai_response.count('*')
        if asterisk_count % 2 != 0:
            ai_response += '*'
        
        # Ensure newlines for readability
        ai_response = re.sub(r'\n{3,}', '\n\n', ai_response)
        
        return ai_response.strip()
    
    def process_article(self, content: str) -> Optional[str]:
        """
        Complete AI analysis pipeline.
        
        Args:
            content: Article content
            
        Returns:
            Formatted AI analysis or None if error
        """
        logger.info("Starting AI analysis pipeline")
        
        if not content:
            logger.error("No content provided for analysis")
            return None
        
        # Analyze with OpenAI
        analysis = self.analyze_with_openai(content)
        if not analysis:
            return None
        
        # Format response
        formatted = self.format_response(analysis)
        
        logger.info("AI analysis pipeline complete")
        return formatted