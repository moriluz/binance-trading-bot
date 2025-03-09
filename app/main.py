"""
Main module for the trading bot.

This module is the entry point for the FastAPI application.
"""

import asyncio
import logging
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from app.config import get_config, validate_config
from app.bot import TradingBot
from app.api.routes import router as api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Binance Trading Bot",
    description="A trading bot for Binance spot trading",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
bot_instance = None

# Include API routes
app.include_router(api_router, prefix="/api")

# Root route
@app.get("/", response_model=Dict[str, str])
async def root():
    return {"message": "Welcome to the Binance Trading Bot"}

# Start bot route
@app.post("/start", response_model=Dict[str, str])
async def start_bot(background_tasks: BackgroundTasks):
    global bot_instance
    
    if bot_instance is not None and bot_instance.is_running:
        return {"message": "Bot is already running"}
    
    # Validate configuration
    if not validate_config():
        raise HTTPException(
            status_code=500,
            detail="Bot is not properly configured. Check the logs for details.",
        )
    
    # Get configuration
    config = get_config()
    
    # Create bot instance
    bot_instance = TradingBot(config)
    
    # Start the bot in a background task
    background_tasks.add_task(bot_instance.run)
    
    return {"message": "Bot started successfully"}

# Stop bot route
@app.post("/stop", response_model=Dict[str, str])
async def stop_bot():
    global bot_instance
    
    if bot_instance is None or not bot_instance.is_running:
        return {"message": "Bot is already stopped"}
    
    # Stop the bot
    bot_instance.stop()
    
    return {"message": "Bot stopped successfully"}

# Run the application
def run_app():
    """
    Run the FastAPI application.
    """
    import uvicorn
    
    config = get_config()
    uvicorn.run(
        "app.main:app",
        host=config["api"]["host"],
        port=config["api"]["port"],
        reload=True,
    )

# Run the bot directly (without API)
async def run_bot():
    """
    Run the trading bot directly (without API).
    """
    # Validate configuration
    if not validate_config():
        logger.error("Bot is not properly configured. Check the logs for details.")
        return
    
    # Get configuration
    config = get_config()
    
    # Create bot instance
    bot = TradingBot(config)
    
    # Run the bot
    await bot.run()

# Entry point
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "bot":
        # Run the bot directly
        asyncio.run(run_bot())
    else:
        # Run the FastAPI application
        run_app()
