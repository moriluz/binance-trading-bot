"""
Base strategy module for the trading bot.

This module provides a base class for all trading strategies.
"""

import logging
import pandas as pd
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)

class BaseStrategy(ABC):
    """
    Base class for all trading strategies.
    
    This class defines the interface for all trading strategies.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the strategy.
        
        Args:
            config (Dict[str, Any]): Configuration dictionary.
        """
        self.config = config
        self.name = "BaseStrategy"
        logger.info(f"Initialized {self.name} strategy")
    
    @abstractmethod
    def generate_signals(self, data: Dict[str, pd.DataFrame]) -> Dict[str, int]:
        """
        Generate trading signals for all symbols.
        
        Args:
            data (Dict[str, pd.DataFrame]): Dictionary of DataFrames with technical indicators.
        
        Returns:
            Dict[str, int]: Dictionary of signals (1 for buy, -1 for sell, 0 for no signal).
        """
        pass
    
    @abstractmethod
    def should_buy(self, symbol: str, data: pd.DataFrame) -> bool:
        """
        Check if we should buy a symbol.
        
        Args:
            symbol (str): Trading pair symbol (e.g., 'BTC/USDT').
            data (pd.DataFrame): DataFrame with technical indicators.
        
        Returns:
            bool: True if we should buy, False otherwise.
        """
        pass
    
    @abstractmethod
    def should_sell(self, symbol: str, data: pd.DataFrame) -> bool:
        """
        Check if we should sell a symbol.
        
        Args:
            symbol (str): Trading pair symbol (e.g., 'BTC/USDT').
            data (pd.DataFrame): DataFrame with technical indicators.
        
        Returns:
            bool: True if we should sell, False otherwise.
        """
        pass
    
    def get_stop_loss(self, symbol: str, entry_price: float) -> float:
        """
        Get the stop loss price for a symbol.
        
        Args:
            symbol (str): Trading pair symbol (e.g., 'BTC/USDT').
            entry_price (float): Entry price.
        
        Returns:
            float: Stop loss price.
        """
        stop_loss_percentage = self.config["trading"]["stop_loss_percentage"]
        return entry_price * (1 - stop_loss_percentage / 100)
    
    def get_take_profit(self, symbol: str, entry_price: float) -> float:
        """
        Get the take profit price for a symbol.
        
        Args:
            symbol (str): Trading pair symbol (e.g., 'BTC/USDT').
            entry_price (float): Entry price.
        
        Returns:
            float: Take profit price.
        """
        take_profit_percentage = self.config["trading"]["take_profit_percentage"]
        return entry_price * (1 + take_profit_percentage / 100)
    
    def get_position_size(self, symbol: str, price: float) -> float:
        """
        Get the position size for a symbol.
        
        Args:
            symbol (str): Trading pair symbol (e.g., 'BTC/USDT').
            price (float): Current price.
        
        Returns:
            float: Position size.
        """
        investment_amount = self.config["trading"]["investment_amount"]
        risk_percentage = self.config["trading"]["risk_percentage"]
        max_position_size = self.config["trading"]["max_position_size"]
        
        # Calculate position size based on risk percentage
        position_size = (investment_amount * risk_percentage / 100) / len(self.config["trading"]["pairs"])
        
        # Limit position size to max_position_size
        position_size = min(position_size, max_position_size)
        
        # Convert to asset amount
        asset_amount = position_size / price
        
        return asset_amount
