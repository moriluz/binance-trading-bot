"""
Configuration module for the trading bot.

This module loads configuration from the .env file and provides it to the rest of the application.
"""

import os
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Binance API Configuration
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

# Trading Configuration
TRADING_PAIRS = os.getenv("TRADING_PAIRS", "BTC/USDT,ETH/USDT,XRP/USDT,ADA/USDT,SOL/USDT").split(",")
INVESTMENT_AMOUNT = float(os.getenv("INVESTMENT_AMOUNT", "100"))
RISK_PERCENTAGE = float(os.getenv("RISK_PERCENTAGE", "50"))
MAX_POSITION_SIZE = float(os.getenv("MAX_POSITION_SIZE", "10"))
STOP_LOSS_PERCENTAGE = float(os.getenv("STOP_LOSS_PERCENTAGE", "5"))
TAKE_PROFIT_PERCENTAGE = float(os.getenv("TAKE_PROFIT_PERCENTAGE", "10"))

# Technical Indicators
SHORT_MA_PERIOD = int(os.getenv("SHORT_MA_PERIOD", "20"))
LONG_MA_PERIOD = int(os.getenv("LONG_MA_PERIOD", "50"))
RSI_PERIOD = int(os.getenv("RSI_PERIOD", "14"))
RSI_BUY_THRESHOLD = float(os.getenv("RSI_BUY_THRESHOLD", "50"))
RSI_SELL_THRESHOLD = float(os.getenv("RSI_SELL_THRESHOLD", "70"))

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./trading_bot.db")

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# Timeframe for data collection (in minutes)
TIMEFRAME = os.getenv("TIMEFRAME", "15m")  # 15 minutes by default

def get_config() -> Dict[str, Any]:
    """
    Get the configuration as a dictionary.
    
    Returns:
        Dict[str, Any]: The configuration dictionary.
    """
    return {
        "binance": {
            "api_key": BINANCE_API_KEY,
            "api_secret": BINANCE_API_SECRET,
        },
        "trading": {
            "pairs": TRADING_PAIRS,
            "investment_amount": INVESTMENT_AMOUNT,
            "risk_percentage": RISK_PERCENTAGE,
            "max_position_size": MAX_POSITION_SIZE,
            "stop_loss_percentage": STOP_LOSS_PERCENTAGE,
            "take_profit_percentage": TAKE_PROFIT_PERCENTAGE,
            "timeframe": TIMEFRAME,
        },
        "indicators": {
            "short_ma_period": SHORT_MA_PERIOD,
            "long_ma_period": LONG_MA_PERIOD,
            "rsi_period": RSI_PERIOD,
            "rsi_buy_threshold": RSI_BUY_THRESHOLD,
            "rsi_sell_threshold": RSI_SELL_THRESHOLD,
        },
        "telegram": {
            "bot_token": TELEGRAM_BOT_TOKEN,
            "chat_id": TELEGRAM_CHAT_ID,
        },
        "database": {
            "url": DATABASE_URL,
        },
        "api": {
            "host": API_HOST,
            "port": API_PORT,
        },
    }

def validate_config() -> bool:
    """
    Validate the configuration.
    
    Returns:
        bool: True if the configuration is valid, False otherwise.
    """
    # Check if Binance API keys are set
    if not BINANCE_API_KEY or not BINANCE_API_SECRET:
        print("Warning: Binance API keys are not set. The bot will not be able to trade.")
        return False
    
    # Check if Telegram configuration is set
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Warning: Telegram configuration is not set. The bot will not be able to send notifications.")
    
    return True
