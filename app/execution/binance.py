"""
Binance API wrapper module for the trading bot.

This module provides a wrapper for the Binance API.
"""

import logging
import ccxt
from typing import Dict, List, Any, Optional
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class BinanceAPI:
    """
    Binance API wrapper.
    
    This class provides a wrapper for the Binance API.
    """
    
    def __init__(self, api_key: str, api_secret: str):
        """
        Initialize the Binance API wrapper.
        
        Args:
            api_key (str): Binance API key.
            api_secret (str): Binance API secret.
        """
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot',
            },
        })
        
        logger.info("Binance API wrapper initialized")
    
    def get_balance(self) -> Dict[str, Any]:
        """
        Get account balance from Binance.
        
        Returns:
            Dict[str, Any]: Account balance.
        """
        try:
            balance = self.exchange.fetch_balance()
            logger.info("Fetched account balance")
            return balance
        except Exception as e:
            logger.exception(f"Error fetching balance: {e}")
            raise
    
    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """
        Get current ticker data from Binance.
        
        Args:
            symbol (str): Trading pair symbol (e.g., 'BTC/USDT').
        
        Returns:
            Dict[str, Any]: Ticker data.
        """
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            logger.info(f"Fetched ticker for {symbol}")
            return ticker
        except Exception as e:
            logger.exception(f"Error fetching ticker: {e}")
            raise
    
    def create_market_buy_order(self, symbol: str, amount: float) -> Dict[str, Any]:
        """
        Create a market buy order on Binance.
        
        Args:
            symbol (str): Trading pair symbol (e.g., 'BTC/USDT').
            amount (float): Amount to buy.
        
        Returns:
            Dict[str, Any]: Order data.
        """
        try:
            order = self.exchange.create_market_buy_order(symbol, amount)
            logger.info(f"Created market buy order for {amount} {symbol}")
            return order
        except Exception as e:
            logger.exception(f"Error creating market buy order: {e}")
            raise
    
    def create_market_sell_order(self, symbol: str, amount: float) -> Dict[str, Any]:
        """
        Create a market sell order on Binance.
        
        Args:
            symbol (str): Trading pair symbol (e.g., 'BTC/USDT').
            amount (float): Amount to sell.
        
        Returns:
            Dict[str, Any]: Order data.
        """
        try:
            order = self.exchange.create_market_sell_order(symbol, amount)
            logger.info(f"Created market sell order for {amount} {symbol}")
            return order
        except Exception as e:
            logger.exception(f"Error creating market sell order: {e}")
            raise
    
    def create_limit_buy_order(self, symbol: str, amount: float, price: float) -> Dict[str, Any]:
        """
        Create a limit buy order on Binance.
        
        Args:
            symbol (str): Trading pair symbol (e.g., 'BTC/USDT').
            amount (float): Amount to buy.
            price (float): Price to buy at.
        
        Returns:
            Dict[str, Any]: Order data.
        """
        try:
            order = self.exchange.create_limit_buy_order(symbol, amount, price)
            logger.info(f"Created limit buy order for {amount} {symbol} at {price}")
            return order
        except Exception as e:
            logger.exception(f"Error creating limit buy order: {e}")
            raise
    
    def create_limit_sell_order(self, symbol: str, amount: float, price: float) -> Dict[str, Any]:
        """
        Create a limit sell order on Binance.
        
        Args:
            symbol (str): Trading pair symbol (e.g., 'BTC/USDT').
            amount (float): Amount to sell.
            price (float): Price to sell at.
        
        Returns:
            Dict[str, Any]: Order data.
        """
        try:
            order = self.exchange.create_limit_sell_order(symbol, amount, price)
            logger.info(f"Created limit sell order for {amount} {symbol} at {price}")
            return order
        except Exception as e:
            logger.exception(f"Error creating limit sell order: {e}")
            raise
    
    def cancel_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """
        Cancel an order on Binance.
        
        Args:
            order_id (str): Order ID.
            symbol (str): Trading pair symbol (e.g., 'BTC/USDT').
        
        Returns:
            Dict[str, Any]: Order data.
        """
        try:
            order = self.exchange.cancel_order(order_id, symbol)
            logger.info(f"Cancelled order {order_id} for {symbol}")
            return order
        except Exception as e:
            logger.exception(f"Error cancelling order: {e}")
            raise
    
    def get_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """
        Get an order from Binance.
        
        Args:
            order_id (str): Order ID.
            symbol (str): Trading pair symbol (e.g., 'BTC/USDT').
        
        Returns:
            Dict[str, Any]: Order data.
        """
        try:
            order = self.exchange.fetch_order(order_id, symbol)
            logger.info(f"Fetched order {order_id} for {symbol}")
            return order
        except Exception as e:
            logger.exception(f"Error fetching order: {e}")
            raise
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get open orders from Binance.
        
        Args:
            symbol (str, optional): Trading pair symbol (e.g., 'BTC/USDT'). Defaults to None.
        
        Returns:
            List[Dict[str, Any]]: Open orders.
        """
        try:
            orders = self.exchange.fetch_open_orders(symbol)
            logger.info(f"Fetched {len(orders)} open orders")
            return orders
        except Exception as e:
            logger.exception(f"Error fetching open orders: {e}")
            raise
    
    def get_closed_orders(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Get closed orders from Binance.
        
        Args:
            symbol (str): Trading pair symbol (e.g., 'BTC/USDT').
        
        Returns:
            List[Dict[str, Any]]: Closed orders.
        """
        try:
            orders = self.exchange.fetch_closed_orders(symbol)
            logger.info(f"Fetched {len(orders)} closed orders for {symbol}")
            return orders
        except Exception as e:
            logger.exception(f"Error fetching closed orders: {e}")
            raise
    
    def get_my_trades(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Get trades from Binance.
        
        Args:
            symbol (str): Trading pair symbol (e.g., 'BTC/USDT').
        
        Returns:
            List[Dict[str, Any]]: Trades.
        """
        try:
            trades = self.exchange.fetch_my_trades(symbol)
            logger.info(f"Fetched {len(trades)} trades for {symbol}")
            return trades
        except Exception as e:
            logger.exception(f"Error fetching trades: {e}")
            raise
