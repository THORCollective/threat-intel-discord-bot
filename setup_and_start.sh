#!/bin/bash

# Setup and start Discord bot test
echo "🤖 Setting up Discord Bot Test Environment"
echo "========================================="

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing requirements..."
pip install -r requirements.txt

echo ""
echo "✅ Environment ready!"
echo ""
echo "To test Discord connection, run:"
echo "source venv/bin/activate && python test_discord_connection.py"
echo ""
echo "You'll need to set your environment variables first:"
echo "export DISCORD_BOT_TOKEN='your_bot_token_here'"
echo "export DISCORD_CHANNEL_ID='1332616096825606164'"