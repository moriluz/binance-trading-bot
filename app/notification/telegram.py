"""
Telegram notification module for the trading bot.

This module provides a class for sending Telegram notifications.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional
from telegram import Bot
from telegram.error import TelegramError

logger = logging.getLogger(__name__)

class TelegramNotifier:
    """
    Telegram notifier.
    
    This class is responsible for sending Telegram notifications.
    """
    
    def __init__(self, token: str, chat_id: str):
        """
        Initialize the Telegram notifier.
        
        Args:
            token (str): Telegram bot token.
            chat_id (str): Telegram chat ID.
        """
        self.token = token
        self.chat_id = chat_id
        self.bot = Bot(token=token)
        
        logger.info("Telegram notifier initialized")
    
    async def send_message(self, message: str) -> None:
        """
        Send a message to Telegram.
        
        Args:
            message (str): Message to send.
        """
        try:
            await self.bot.send_message(chat_id=self.chat_id, text=message)
            logger.info(f"Sent Telegram message: {message}")
        except TelegramError as e:
            logger.exception(f"Error sending Telegram message: {e}")
            raise
    
    async def send_trade_notification(self, trade_type: str, symbol: str, amount: float, price: float) -> None:
        """
        Send a trade notification to Telegram.
        
        Args:
            trade_type (str): Trade type ('buy' or 'sell').
            symbol (str): Trading pair symbol (e.g., 'BTC/USDT').
            amount (float): Amount of the asset.
            price (float): Price of the asset.
        """
        try:
            message = f"🤖 *TRADE ALERT*\n\n"
            
            if trade_type.lower() == "buy":
                message += f"✅ *BUY* {amount} {symbol} at ${price:.2f}\n"
            elif trade_type.lower() == "sell":
                message += f"🔴 *SELL* {amount} {symbol} at ${price:.2f}\n"
            
            message += f"💰 Total: ${amount * price:.2f}"
            
            await self.send_message(message)
        except Exception as e:
            logger.exception(f"Error sending trade notification: {e}")
            raise
    
    async def send_signal_notification(self, signal_type: str, symbol: str, price: float, indicators: Dict[str, float]) -> None:
        """
        Send a signal notification to Telegram.
        
        Args:
            signal_type (str): Signal type ('buy' or 'sell').
            symbol (str): Trading pair symbol (e.g., 'BTC/USDT').
            price (float): Price of the asset.
            indicators (Dict[str, float]): Dictionary of indicators.
        """
        try:
            message = f"🤖 *SIGNAL ALERT*\n\n"
            
            if signal_type.lower() == "buy":
                message += f"🟢 *BUY SIGNAL* for {symbol} at ${price:.2f}\n\n"
            elif signal_type.lower() == "sell":
                message += f"🔴 *SELL SIGNAL* for {symbol} at ${price:.2f}\n\n"
            
            message += "*Indicators:*\n"
            for indicator, value in indicators.items():
                message += f"- {indicator}: {value:.2f}\n"
            
            await self.send_message(message)
        except Exception as e:
            logger.exception(f"Error sending signal notification: {e}")
            raise
    
    async def send_error_notification(self, error_message: str) -> None:
        """
        Send an error notification to Telegram.
        
        Args:
            error_message (str): Error message.
        """
        try:
            message = f"🤖 *ERROR ALERT*\n\n"
            message += f"❌ {error_message}"
            
            await self.send_message(message)
        except Exception as e:
            logger.exception(f"Error sending error notification: {e}")
            raise
    
    async def send_portfolio_notification(self, positions: List[Dict[str, Any]], total_value: float, profit_loss: float) -> None:
        """
        Send a portfolio notification to Telegram.
        
        Args:
            positions (List[Dict[str, Any]]): List of positions.
            total_value (float): Total portfolio value.
            profit_loss (float): Total profit/loss.
        """
        try:
            message = f"🤖 *PORTFOLIO UPDATE*\n\n"
            
            message += f"💰 *Total Value:* ${total_value:.2f}\n"
            message += f"📈 *Profit/Loss:* ${profit_loss:.2f} ({profit_loss / total_value * 100:.2f}%)\n\n"
            
            message += "*Positions:*\n"
            for position in positions:
                symbol = position["symbol"]
                amount = position["amount"]
                entry_price = position["entry_price"]
                current_price = position["current_price"]
                profit_loss = position["profit_loss"]
                profit_loss_percentage = position["profit_loss_percentage"]
                
                message += f"- {symbol}: {amount} @ ${entry_price:.2f} (Current: ${current_price:.2f})\n"
                message += f"  P/L: ${profit_loss:.2f} ({profit_loss_percentage:.2f}%)\n"
            
            await self.send_message(message)
        except Exception as e:
            logger.exception(f"Error sending portfolio notification: {e}")
            raise
    
    async def send_status_notification(self, status: str) -> None:
        """
        Send a status notification to Telegram.
        
        Args:
            status (str): Status message.
        """
        try:
            message = f"🤖 *STATUS UPDATE*\n\n"
            message += f"ℹ️ {status}"
            
            await self.send_message(message)
        except Exception as e:
            logger.exception(f"Error sending status notification: {e}")
            raise

def create_telegram_notifier(config: Dict[str, Any]) -> Optional[TelegramNotifier]:
    """
    Create a Telegram notifier.
    
    Args:
        config (Dict[str, Any]): Configuration dictionary.
    
    Returns:
        Optional[TelegramNotifier]: Telegram notifier.
    """
    try:
        token = config["telegram"]["bot_token"]
        chat_id = config["telegram"]["chat_id"]
        
        if not token or not chat_id:
            logger.warning("Telegram configuration is not set. Notifications will not be sent.")
            return None
        
        return TelegramNotifier(token, chat_id)
    except Exception as e:
        logger.exception(f"Error creating Telegram notifier: {e}")
        return None
