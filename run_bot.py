#!/usr/bin/env python3
"""
Run script for the trading bot.

This script runs the trading bot directly from the command line.
"""

import asyncio
import argparse
import logging
import signal
import sys

from app.config import get_config, validate_config
from app.bot import TradingBot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Global variables
bot_instance = None

async def run_bot():
    """
    Run the trading bot.
    """
    global bot_instance
    
    # Validate configuration
    if not validate_config():
        logger.error("Bot is not properly configured. Check the logs for details.")
        return
    
    # Get configuration
    config = get_config()
    
    # Create bot instance
    bot_instance = TradingBot(config)
    
    # Set up signal handlers
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(stop_bot()))
    
    # Run the bot
    logger.info("Starting the trading bot...")
    await bot_instance.run()

async def stop_bot():
    """
    Stop the trading bot.
    """
    global bot_instance
    
    if bot_instance is not None:
        logger.info("Stopping the trading bot...")
        bot_instance.stop()
    
    # Exit the program
    sys.exit(0)

def parse_args():
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Run the trading bot.")
    
    parser.add_argument(
        "--config",
        type=str,
        default=".env",
        help="Path to the configuration file.",
    )
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    
    # Run the bot
    asyncio.run(run_bot())
