"""
Data collector module for the trading bot.

This module is responsible for collecting data from Binance.
"""

import logging
import pandas as pd
import ccxt
from typing import Dict, List, Any, Optional
import time
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class BinanceDataCollector:
    """
    Data collector for Binance.
    
    This class is responsible for collecting data from Binance.
    """
    
    def __init__(self, api_key: str = None, api_secret: str = None):
        """
        Initialize the data collector.
        
        Args:
            api_key (str, optional): Binance API key. Defaults to None.
            api_secret (str, optional): Binance API secret. Defaults to None.
        """
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot',
            },
        })
        
        # Check if the exchange is available
        if not self.exchange.has['fetchOHLCV']:
            raise Exception("Exchange does not support OHLCV data")
        
        logger.info("Binance data collector initialized")
    
    def get_historical_data(
        self,
        symbol: str,
        timeframe: str = '15m',
        limit: int = 100,
        since: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Get historical OHLCV data from Binance.
        
        Args:
            symbol (str): Trading pair symbol (e.g., 'BTC/USDT').
            timeframe (str, optional): Timeframe. Defaults to '15m'.
            limit (int, optional): Number of candles to fetch. Defaults to 100.
            since (int, optional): Timestamp in milliseconds. Defaults to None.
        
        Returns:
            pd.DataFrame: DataFrame with OHLCV data.
        """
        try:
            # Fetch OHLCV data
            ohlcv = self.exchange.fetch_ohlcv(
                symbol=symbol,
                timeframe=timeframe,
                limit=limit,
                since=since,
            )
            
            # Convert to DataFrame
            df = pd.DataFrame(
                ohlcv,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'],
            )
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # Set timestamp as index
            df.set_index('timestamp', inplace=True)
            
            logger.info(f"Fetched {len(df)} candles for {symbol} ({timeframe})")
            
            return df
        except Exception as e:
            logger.exception(f"Error fetching historical data: {e}")
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
    
    def get_order_book(self, symbol: str, limit: int = 20) -> Dict[str, Any]:
        """
        Get order book from Binance.
        
        Args:
            symbol (str): Trading pair symbol (e.g., 'BTC/USDT').
            limit (int, optional): Number of orders to fetch. Defaults to 20.
        
        Returns:
            Dict[str, Any]: Order book.
        """
        try:
            order_book = self.exchange.fetch_order_book(symbol, limit)
            logger.info(f"Fetched order book for {symbol}")
            return order_book
        except Exception as e:
            logger.exception(f"Error fetching order book: {e}")
            raise
    
    def get_trades(self, symbol: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get recent trades from Binance.
        
        Args:
            symbol (str): Trading pair symbol (e.g., 'BTC/USDT').
            limit (int, optional): Number of trades to fetch. Defaults to 20.
        
        Returns:
            List[Dict[str, Any]]: Recent trades.
        """
        try:
            trades = self.exchange.fetch_trades(symbol, limit)
            logger.info(f"Fetched {len(trades)} trades for {symbol}")
            return trades
        except Exception as e:
            logger.exception(f"Error fetching trades: {e}")
            raise
