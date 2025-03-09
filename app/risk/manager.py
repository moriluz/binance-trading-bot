"""
Risk management module for the trading bot.

This module provides a class for managing risk.
"""

import logging
from typing import Dict, List, Any, Optional
import pandas as pd

logger = logging.getLogger(__name__)

class RiskManager:
    """
    Risk manager.
    
    This class is responsible for managing risk.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the risk manager.
        
        Args:
            config (Dict[str, Any]): Configuration dictionary.
        """
        self.config = config
        self.positions = {}  # Dictionary to store positions
        
        # Get risk parameters from config
        self.investment_amount = config["trading"]["investment_amount"]
        self.risk_percentage = config["trading"]["risk_percentage"]
        self.max_position_size = config["trading"]["max_position_size"]
        self.stop_loss_percentage = config["trading"]["stop_loss_percentage"]
        self.take_profit_percentage = config["trading"]["take_profit_percentage"]
        
        logger.info("Risk manager initialized")
    
    def calculate_position_size(self, symbol: str, price: float) -> float:
        """
        Calculate the position size for a symbol.
        
        Args:
            symbol (str): Trading pair symbol (e.g., 'BTC/USDT').
            price (float): Current price.
        
        Returns:
            float: Position size.
        """
        try:
            # Calculate position size based on risk percentage
            position_size = (self.investment_amount * self.risk_percentage / 100) / len(self.config["trading"]["pairs"])
            
            # Limit position size to max_position_size
            position_size = min(position_size, self.max_position_size)
            
            # Convert to asset amount
            asset_amount = position_size / price
            
            logger.info(f"Calculated position size for {symbol}: {asset_amount} (${position_size:.2f})")
            
            return asset_amount
        except Exception as e:
            logger.exception(f"Error calculating position size: {e}")
            raise
    
    def calculate_stop_loss(self, symbol: str, entry_price: float) -> float:
        """
        Calculate the stop loss price for a symbol.
        
        Args:
            symbol (str): Trading pair symbol (e.g., 'BTC/USDT').
            entry_price (float): Entry price.
        
        Returns:
            float: Stop loss price.
        """
        try:
            stop_loss_price = entry_price * (1 - self.stop_loss_percentage / 100)
            
            logger.info(f"Calculated stop loss for {symbol}: {stop_loss_price:.2f}")
            
            return stop_loss_price
        except Exception as e:
            logger.exception(f"Error calculating stop loss: {e}")
            raise
    
    def calculate_take_profit(self, symbol: str, entry_price: float) -> float:
        """
        Calculate the take profit price for a symbol.
        
        Args:
            symbol (str): Trading pair symbol (e.g., 'BTC/USDT').
            entry_price (float): Entry price.
        
        Returns:
            float: Take profit price.
        """
        try:
            take_profit_price = entry_price * (1 + self.take_profit_percentage / 100)
            
            logger.info(f"Calculated take profit for {symbol}: {take_profit_price:.2f}")
            
            return take_profit_price
        except Exception as e:
            logger.exception(f"Error calculating take profit: {e}")
            raise
    
    def add_position(self, symbol: str, amount: float, entry_price: float) -> Dict[str, Any]:
        """
        Add a position.
        
        Args:
            symbol (str): Trading pair symbol (e.g., 'BTC/USDT').
            amount (float): Amount of the asset.
            entry_price (float): Entry price.
        
        Returns:
            Dict[str, Any]: Position data.
        """
        try:
            # Calculate stop loss and take profit
            stop_loss = self.calculate_stop_loss(symbol, entry_price)
            take_profit = self.calculate_take_profit(symbol, entry_price)
            
            # Create the position
            position = {
                "symbol": symbol,
                "amount": amount,
                "entry_price": entry_price,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "current_price": entry_price,
                "profit_loss": 0.0,
                "profit_loss_percentage": 0.0,
            }
            
            # Store the position
            self.positions[symbol] = position
            
            logger.info(f"Added position for {symbol}: {amount} at {entry_price:.2f}")
            
            return position
        except Exception as e:
            logger.exception(f"Error adding position: {e}")
            raise
    
    def update_position(self, symbol: str, current_price: float) -> Dict[str, Any]:
        """
        Update a position.
        
        Args:
            symbol (str): Trading pair symbol (e.g., 'BTC/USDT').
            current_price (float): Current price.
        
        Returns:
            Dict[str, Any]: Position data.
        """
        try:
            # Get the position
            position = self.positions.get(symbol)
            if position is None:
                raise ValueError(f"Position for {symbol} not found")
            
            # Update the position
            position["current_price"] = current_price
            position["profit_loss"] = (current_price - position["entry_price"]) * position["amount"]
            position["profit_loss_percentage"] = (current_price / position["entry_price"] - 1) * 100
            
            logger.info(f"Updated position for {symbol}: {position['amount']} at {current_price:.2f} "
                       f"(P/L: ${position['profit_loss']:.2f}, {position['profit_loss_percentage']:.2f}%)")
            
            return position
        except Exception as e:
            logger.exception(f"Error updating position: {e}")
            raise
    
    def remove_position(self, symbol: str) -> Dict[str, Any]:
        """
        Remove a position.
        
        Args:
            symbol (str): Trading pair symbol (e.g., 'BTC/USDT').
        
        Returns:
            Dict[str, Any]: Position data.
        """
        try:
            # Get the position
            position = self.positions.get(symbol)
            if position is None:
                raise ValueError(f"Position for {symbol} not found")
            
            # Remove the position
            del self.positions[symbol]
            
            logger.info(f"Removed position for {symbol}")
            
            return position
        except Exception as e:
            logger.exception(f"Error removing position: {e}")
            raise
    
    def get_position(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get a position.
        
        Args:
            symbol (str): Trading pair symbol (e.g., 'BTC/USDT').
        
        Returns:
            Optional[Dict[str, Any]]: Position data.
        """
        return self.positions.get(symbol)
    
    def get_all_positions(self) -> List[Dict[str, Any]]:
        """
        Get all positions.
        
        Returns:
            List[Dict[str, Any]]: All positions.
        """
        return list(self.positions.values())
    
    def check_stop_loss(self, symbol: str, current_price: float) -> bool:
        """
        Check if the stop loss has been triggered.
        
        Args:
            symbol (str): Trading pair symbol (e.g., 'BTC/USDT').
            current_price (float): Current price.
        
        Returns:
            bool: True if the stop loss has been triggered, False otherwise.
        """
        try:
            # Get the position
            position = self.positions.get(symbol)
            if position is None:
                return False
            
            # Check if the stop loss has been triggered
            if current_price <= position["stop_loss"]:
                logger.info(f"Stop loss triggered for {symbol} at {current_price:.2f}")
                return True
            
            return False
        except Exception as e:
            logger.exception(f"Error checking stop loss: {e}")
            raise
    
    def check_take_profit(self, symbol: str, current_price: float) -> bool:
        """
        Check if the take profit has been triggered.
        
        Args:
            symbol (str): Trading pair symbol (e.g., 'BTC/USDT').
            current_price (float): Current price.
        
        Returns:
            bool: True if the take profit has been triggered, False otherwise.
        """
        try:
            # Get the position
            position = self.positions.get(symbol)
            if position is None:
                return False
            
            # Check if the take profit has been triggered
            if current_price >= position["take_profit"]:
                logger.info(f"Take profit triggered for {symbol} at {current_price:.2f}")
                return True
            
            return False
        except Exception as e:
            logger.exception(f"Error checking take profit: {e}")
            raise
    
    def calculate_portfolio_value(self, prices: Dict[str, float]) -> float:
        """
        Calculate the portfolio value.
        
        Args:
            prices (Dict[str, float]): Dictionary of current prices.
        
        Returns:
            float: Portfolio value.
        """
        try:
            portfolio_value = 0.0
            
            for symbol, position in self.positions.items():
                if symbol in prices:
                    portfolio_value += position["amount"] * prices[symbol]
            
            logger.info(f"Calculated portfolio value: ${portfolio_value:.2f}")
            
            return portfolio_value
        except Exception as e:
            logger.exception(f"Error calculating portfolio value: {e}")
            raise
    
    def calculate_portfolio_profit_loss(self, prices: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate the portfolio profit/loss.
        
        Args:
            prices (Dict[str, float]): Dictionary of current prices.
        
        Returns:
            Dict[str, float]: Portfolio profit/loss.
        """
        try:
            total_profit_loss = 0.0
            total_profit_loss_percentage = 0.0
            
            for symbol, position in self.positions.items():
                if symbol in prices:
                    # Update the position
                    self.update_position(symbol, prices[symbol])
                    
                    # Add to total profit/loss
                    total_profit_loss += position["profit_loss"]
            
            # Calculate total profit/loss percentage
            if self.investment_amount > 0:
                total_profit_loss_percentage = (total_profit_loss / self.investment_amount) * 100
            
            logger.info(f"Calculated portfolio profit/loss: ${total_profit_loss:.2f} ({total_profit_loss_percentage:.2f}%)")
            
            return {
                "profit_loss": total_profit_loss,
                "profit_loss_percentage": total_profit_loss_percentage,
            }
        except Exception as e:
            logger.exception(f"Error calculating portfolio profit/loss: {e}")
            raise
