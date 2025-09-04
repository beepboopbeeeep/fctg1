#!/bin/bash

# Shazam Telegram Bot Start Script

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the script directory
cd "$SCRIPT_DIR"

# Find Python command
if command -v python3.13 &> /dev/null; then
    PYTHON_CMD="python3.13"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    echo "❌ Python 3 not found. Please install Python 3.13 first."
    exit 1
fi

echo "🎵 Starting Shazam Telegram Bot..."
echo "Using Python: $PYTHON_CMD"
echo "Press Ctrl+C to stop the bot"
echo ""

# Start the bot
$PYTHON_CMD shazam_bot.py