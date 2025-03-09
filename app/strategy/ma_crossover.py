"""
Moving Average Crossover with RSI Confirmation strategy module for the trading bot.

This module implements the Moving Average Crossover with RSI Confirmation strategy.
"""

import logging
import pandas as pd
from typing import Dict, Any

from app.strategy.base import BaseStrategy
from app.data.indicators import TechnicalIndicators

logger = logging.getLogger(__name__)

class MACrossoverStrategy(BaseStrategy):
    """
    Moving Average Crossover with RSI Confirmation strategy.
    
    This strategy generates buy signals when the short MA crosses above the long MA
    and the RSI is between 30 and 50. It generates sell signals when the short MA
    crosses below the long MA and the RSI is above 70.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the strategy.
        
        Args:
            config (Dict[str, Any]): Configuration dictionary.
        """
        super().__init__(config)
        self.name = "MACrossoverStrategy"
        
        # Get indicator parameters from config
        self.short_ma_period = config["indicators"]["short_ma_period"]
        self.long_ma_period = config["indicators"]["long_ma_period"]
        self.rsi_period = config["indicators"]["rsi_period"]
        self.rsi_buy_threshold = config["indicators"]["rsi_buy_threshold"]
        self.rsi_sell_threshold = config["indicators"]["rsi_sell_threshold"]
        
        logger.info(f"Initialized {self.name} strategy with parameters: "
                   f"short_ma_period={self.short_ma_period}, "
                   f"long_ma_period={self.long_ma_period}, "
                   f"rsi_period={self.rsi_period}, "
                   f"rsi_buy_threshold={self.rsi_buy_threshold}, "
                   f"rsi_sell_threshold={self.rsi_sell_threshold}")
    
    def generate_signals(self, data: Dict[str, pd.DataFrame]) -> Dict[str, int]:
        """
        Generate trading signals for all symbols.
        
        Args:
            data (Dict[str, pd.DataFrame]): Dictionary of DataFrames with technical indicators.
        
        Returns:
            Dict[str, int]: Dictionary of signals (1 for buy, -1 for sell, 0 for no signal).
        """
        signals = {}
        
        for symbol, df in data.items():
            if len(df) < max(self.short_ma_period, self.long_ma_period, self.rsi_period) + 1:
                logger.warning(f"Not enough data for {symbol} to generate signals")
                signals[symbol] = 0
                continue
            
            # Get combined signal
            signal = TechnicalIndicators.get_combined_signal(df, self.config)
            signals[symbol] = signal
            
            if signal == 1:
                logger.info(f"Buy signal for {symbol}")
            elif signal == -1:
                logger.info(f"Sell signal for {symbol}")
        
        return signals
    
    def should_buy(self, symbol: str, data: pd.DataFrame) -> bool:
        """
        Check if we should buy a symbol.
        
        Args:
            symbol (str): Trading pair symbol (e.g., 'BTC/USDT').
            data (pd.DataFrame): DataFrame with technical indicators.
        
        Returns:
            bool: True if we should buy, False otherwise.
        """
        if len(data) < max(self.short_ma_period, self.long_ma_period, self.rsi_period) + 1:
            logger.warning(f"Not enough data for {symbol} to check if we should buy")
            return False
        
        # Get the last two rows
        last_row = data.iloc[-1]
        prev_row = data.iloc[-2]
        
        # Check for MA crossover (bullish)
        ma_crossover = (prev_row[f'ma_{self.short_ma_period}'] <= prev_row[f'ma_{self.long_ma_period}'] and
                        last_row[f'ma_{self.short_ma_period}'] > last_row[f'ma_{self.long_ma_period}'])
        
        # Check RSI
        rsi_condition = last_row['rsi'] >= 30 and last_row['rsi'] <= 50
        
        # Combined condition
        should_buy = ma_crossover and rsi_condition
        
        if should_buy:
            logger.info(f"Should buy {symbol}: MA crossover (bullish) and RSI is {last_row['rsi']:.2f}")
        
        return should_buy
    
    def should_sell(self, symbol: str, data: pd.DataFrame) -> bool:
        """
        Check if we should sell a symbol.
        
        Args:
            symbol (str): Trading pair symbol (e.g., 'BTC/USDT').
            data (pd.DataFrame): DataFrame with technical indicators.
        
        Returns:
            bool: True if we should sell, False otherwise.
        """
        if len(data) < max(self.short_ma_period, self.long_ma_period, self.rsi_period) + 1:
            logger.warning(f"Not enough data for {symbol} to check if we should sell")
            return False
        
        # Get the last two rows
        last_row = data.iloc[-1]
        prev_row = data.iloc[-2]
        
        # Check for MA crossover (bearish)
        ma_crossover = (prev_row[f'ma_{self.short_ma_period}'] >= prev_row[f'ma_{self.long_ma_period}'] and
                        last_row[f'ma_{self.short_ma_period}'] < last_row[f'ma_{self.long_ma_period}'])
        
        # Check RSI
        rsi_condition = last_row['rsi'] >= 70
        
        # Combined condition
        should_sell = ma_crossover or rsi_condition
        
        if should_sell:
            if ma_crossover:
                logger.info(f"Should sell {symbol}: MA crossover (bearish)")
            if rsi_condition:
                logger.info(f"Should sell {symbol}: RSI is {last_row['rsi']:.2f} (overbought)")
        
        return should_sell
