#!/usr/bin/env python3
"""
Shazam Telegram Bot Runner
This script runs the Shazam Telegram Bot with proper error handling
"""

import subprocess
import sys
import os
import signal
import time
import logging
from datetime import datetime

# Set up logging
log_file = 'bot.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info("Received shutdown signal, stopping bot...")
    sys.exit(0)

def run_bot():
    """Run the Shazam bot with auto-restart capability"""
    logger.info(f"Starting Shazam Telegram Bot at {datetime.now()}")
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Change to the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    logger.info(f"Changed working directory to: {script_dir}")
    
    while True:
        try:
            logger.info("Starting bot process...")
            
            # Run the bot
            process = subprocess.Popen(
                [sys.executable, 'shazam_bot.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Monitor the process
            while True:
                return_code = process.poll()
                if return_code is not None:
                    logger.error(f"Bot process exited with code {return_code}")
                    break
                
                # Read output
                if process.stdout:
                    line = process.stdout.readline()
                    if line:
                        logger.info(line.strip())
                
                if process.stderr:
                    line = process.stderr.readline()
                    if line:
                        logger.error(line.strip())
                
                time.sleep(0.1)
            
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            break
        except Exception as e:
            logger.error(f"Error running bot: {e}")
        
        # Wait before restarting
        logger.info("Waiting 10 seconds before restarting...")
        time.sleep(10)

if __name__ == '__main__':
    run_bot()