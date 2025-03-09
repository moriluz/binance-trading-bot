"""
Technical indicators module for the trading bot.

This module is responsible for calculating technical indicators.
"""

import logging
import pandas as pd
import pandas_ta as ta
from typing import Dict, Any

logger = logging.getLogger(__name__)

class TechnicalIndicators:
    """
    Technical indicators calculator.
    
    This class is responsible for calculating technical indicators.
    """
    
    @staticmethod
    def add_indicators(df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """
        Add technical indicators to a DataFrame.
        
        Args:
            df (pd.DataFrame): DataFrame with OHLCV data.
            config (Dict[str, Any]): Configuration dictionary.
        
        Returns:
            pd.DataFrame: DataFrame with technical indicators.
        """
        try:
            # Make a copy of the DataFrame to avoid modifying the original
            df_with_indicators = df.copy()
            
            # Get indicator parameters from config
            short_ma_period = config["indicators"]["short_ma_period"]
            long_ma_period = config["indicators"]["long_ma_period"]
            rsi_period = config["indicators"]["rsi_period"]
            
            # Calculate Moving Averages
            df_with_indicators[f'ma_{short_ma_period}'] = ta.sma(df_with_indicators['close'], length=short_ma_period)
            df_with_indicators[f'ma_{long_ma_period}'] = ta.sma(df_with_indicators['close'], length=long_ma_period)
            
            # Calculate RSI
            df_with_indicators['rsi'] = ta.rsi(df_with_indicators['close'], length=rsi_period)
            
            # Calculate MACD
            macd = ta.macd(df_with_indicators['close'])
            df_with_indicators = pd.concat([df_with_indicators, macd], axis=1)
            
            # Calculate Bollinger Bands
            bbands = ta.bbands(df_with_indicators['close'])
            df_with_indicators = pd.concat([df_with_indicators, bbands], axis=1)
            
            # Drop NaN values
            df_with_indicators.dropna(inplace=True)
            
            logger.info(f"Added technical indicators to DataFrame with {len(df_with_indicators)} rows")
            
            return df_with_indicators
        except Exception as e:
            logger.exception(f"Error adding technical indicators: {e}")
            raise
    
    @staticmethod
    def get_ma_crossover_signal(df: pd.DataFrame, config: Dict[str, Any]) -> int:
        """
        Get Moving Average crossover signal.
        
        Args:
            df (pd.DataFrame): DataFrame with technical indicators.
            config (Dict[str, Any]): Configuration dictionary.
        
        Returns:
            int: Signal (1 for buy, -1 for sell, 0 for no signal).
        """
        try:
            # Get indicator parameters from config
            short_ma_period = config["indicators"]["short_ma_period"]
            long_ma_period = config["indicators"]["long_ma_period"]
            
            # Get the last two rows
            last_row = df.iloc[-1]
            prev_row = df.iloc[-2]
            
            # Check for crossover
            if (prev_row[f'ma_{short_ma_period}'] <= prev_row[f'ma_{long_ma_period}'] and
                last_row[f'ma_{short_ma_period}'] > last_row[f'ma_{long_ma_period}']):
                # Bullish crossover (short MA crosses above long MA)
                return 1
            elif (prev_row[f'ma_{short_ma_period}'] >= prev_row[f'ma_{long_ma_period}'] and
                  last_row[f'ma_{short_ma_period}'] < last_row[f'ma_{long_ma_period}']):
                # Bearish crossover (short MA crosses below long MA)
                return -1
            else:
                # No crossover
                return 0
        except Exception as e:
            logger.exception(f"Error getting MA crossover signal: {e}")
            raise
    
    @staticmethod
    def get_rsi_signal(df: pd.DataFrame, config: Dict[str, Any]) -> int:
        """
        Get RSI signal.
        
        Args:
            df (pd.DataFrame): DataFrame with technical indicators.
            config (Dict[str, Any]): Configuration dictionary.
        
        Returns:
            int: Signal (1 for buy, -1 for sell, 0 for no signal).
        """
        try:
            # Get indicator parameters from config
            rsi_buy_threshold = config["indicators"]["rsi_buy_threshold"]
            rsi_sell_threshold = config["indicators"]["rsi_sell_threshold"]
            
            # Get the last row
            last_row = df.iloc[-1]
            
            # Check RSI value
            if last_row['rsi'] < rsi_buy_threshold:
                # RSI is below buy threshold (oversold)
                return 1
            elif last_row['rsi'] > rsi_sell_threshold:
                # RSI is above sell threshold (overbought)
                return -1
            else:
                # RSI is in the middle
                return 0
        except Exception as e:
            logger.exception(f"Error getting RSI signal: {e}")
            raise
    
    @staticmethod
    def get_combined_signal(df: pd.DataFrame, config: Dict[str, Any]) -> int:
        """
        Get combined signal from multiple indicators.
        
        Args:
            df (pd.DataFrame): DataFrame with technical indicators.
            config (Dict[str, Any]): Configuration dictionary.
        
        Returns:
            int: Signal (1 for buy, -1 for sell, 0 for no signal).
        """
        try:
            # Get individual signals
            ma_signal = TechnicalIndicators.get_ma_crossover_signal(df, config)
            rsi_signal = TechnicalIndicators.get_rsi_signal(df, config)
            
            # Get the last row
            last_row = df.iloc[-1]
            
            # Get indicator parameters from config
            short_ma_period = config["indicators"]["short_ma_period"]
            long_ma_period = config["indicators"]["long_ma_period"]
            rsi_buy_threshold = config["indicators"]["rsi_buy_threshold"]
            rsi_sell_threshold = config["indicators"]["rsi_sell_threshold"]
            
            # Combined signal logic
            if ma_signal == 1 and (rsi_signal == 1 or (last_row['rsi'] >= 30 and last_row['rsi'] <= 50)):
                # Buy signal: MA crossover (bullish) and RSI is not overbought
                logger.info(f"Buy signal: MA crossover (bullish) and RSI is {last_row['rsi']:.2f}")
                return 1
            elif ma_signal == -1 and (rsi_signal == -1 or last_row['rsi'] >= 70):
                # Sell signal: MA crossover (bearish) and RSI is overbought
                logger.info(f"Sell signal: MA crossover (bearish) and RSI is {last_row['rsi']:.2f}")
                return -1
            else:
                # No clear signal
                return 0
        except Exception as e:
            logger.exception(f"Error getting combined signal: {e}")
            raise
