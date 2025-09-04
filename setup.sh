#!/bin/bash

# Shazam Telegram Bot Setup Script
# This script will help you set up the Shazam Telegram Bot

echo "🎵 Shazam Telegram Bot Setup"
echo "================================"

# Check if Python 3.13 is installed
echo "🔍 Checking Python installation..."
if command -v python3.13 &> /dev/null; then
    PYTHON_CMD="python3.13"
    echo "✅ Python 3.13 found: $(python3.13 --version)"
elif command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    echo "⚠️  Python 3.13 not found, but Python 3 found: $PYTHON_VERSION"
    PYTHON_CMD="python3"
    echo "   Using $PYTHON_CMD instead"
else
    echo "❌ Python 3 not found. Please install Python 3.13 first."
    exit 1
fi

# Check if pip is installed
echo "🔍 Checking pip installation..."
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
    echo "✅ pip found: $(pip3 --version)"
elif command -v pip &> /dev/null; then
    PIP_CMD="pip"
    echo "✅ pip found: $(pip --version)"
else
    echo "❌ pip not found. Please install pip first."
    exit 1
fi

# Install required packages
echo "📦 Installing required packages..."
$PIP_CMD install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Packages installed successfully"
else
    echo "❌ Failed to install packages. Please check the error messages above."
    exit 1
fi

# Get bot token from user
echo ""
echo "🤖 Bot Configuration"
echo "===================="
echo "To get your bot token:"
echo "1. Talk to @BotFather on Telegram"
echo "2. Use /newbot command"
echo "3. Follow the instructions to create your bot"
echo "4. Copy the bot token"
echo ""
read -p "Please enter your bot token: " BOT_TOKEN

# Validate bot token
if [[ ! $BOT_TOKEN =~ ^[0-9]{8,10}:[A-Za-z0-9_-]{35}$ ]]; then
    echo "❌ Invalid bot token format. Please check and try again."
    exit 1
fi

# Get admin user ID (optional)
echo ""
read -p "Enter your admin user ID (optional, press Enter to skip): " ADMIN_USER_ID

# Create the bot configuration
echo ""
echo "⚙️  Creating bot configuration..."
sed -i "s/YOUR_BOT_TOKEN_HERE/$BOT_TOKEN/g" shazam_bot.py

if [ ! -z "$ADMIN_USER_ID" ]; then
    sed -i "s/ADMIN_USER_ID = None/ADMIN_USER_ID = $ADMIN_USER_ID/g" shazam_bot.py
    echo "✅ Admin user ID set to: $ADMIN_USER_ID"
else
    echo "ℹ️  No admin user ID provided (this is optional)"
fi

# Create start script
echo ""
echo "🚀 Creating start script..."
cat > start_bot.sh << 'EOF'
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
EOF

chmod +x start_bot.sh

# Create systemd service file (for Linux systems)
echo ""
echo "🔧 Creating systemd service file..."
cat > shazam-bot.service << EOF
[Unit]
Description=Shazam Telegram Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
ExecStart=$(which $PYTHON_CMD) $(pwd)/shazam_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Systemd service file created: shazam-bot.service"

# Create log rotation configuration
echo ""
echo "📝 Creating log rotation configuration..."
cat > logrotate.conf << EOF
$(pwd)/bot.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 $USER $USER
}
EOF

echo "✅ Log rotation configuration created: logrotate.conf"

# Setup complete
echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "Your Shazam Telegram Bot is now configured!"
echo ""
echo "📋 Next Steps:"
echo "1. Test the bot: ./start_bot.sh"
echo "2. Set up systemd service (optional):"
echo "   sudo cp shazam-bot.service /etc/systemd/system/"
echo "   sudo systemctl daemon-reload"
echo "   sudo systemctl enable shazam-bot.service"
echo "   sudo systemctl start shazam-bot.service"
echo "3. Set up log rotation (optional):"
echo "   sudo cp logrotate.conf /etc/logrotate.d/shazam-bot"
echo ""
echo "🔧 Commands:"
echo "- Start bot: ./start_bot.sh"
echo "- Stop bot: Press Ctrl+C"
echo "- View logs: tail -f bot.log"
echo "- Check service status: sudo systemctl status shazam-bot.service"
echo ""
echo "🤖 Bot Features:"
echo "- Music recognition from audio files"
echo "- Inline search in groups"
echo "- Multi-language support (Persian/English)"
echo "- Song information editing"
echo "- Artist and track information"
echo ""
echo "📞 Support:"
echo "If you encounter any issues, please check the logs or contact support."
echo ""
echo "🚀 Happy botting!"