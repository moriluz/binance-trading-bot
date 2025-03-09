"""
API models module for the trading bot.

This module provides the Pydantic models for the API.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class StatusResponse(BaseModel):
    """
    Status response model.
    """
    
    status: str = Field(..., description="Bot status ('running' or 'stopped')")
    running: bool = Field(..., description="Whether the bot is running")
    config: Dict[str, Any] = Field(..., description="Bot configuration")

class TradeResponse(BaseModel):
    """
    Trade response model.
    """
    
    id: str = Field(..., description="Trade ID")
    symbol: str = Field(..., description="Trading pair symbol")
    type: str = Field(..., description="Trade type ('buy' or 'sell')")
    price: float = Field(..., description="Trade price")
    amount: float = Field(..., description="Trade amount")
    timestamp: str = Field(..., description="Trade timestamp")
    status: str = Field(..., description="Trade status")

class BalanceResponse(BaseModel):
    """
    Balance response model.
    """
    
    total_balance: float = Field(..., description="Total balance")
    available_balance: float = Field(..., description="Available balance")
    in_trade: float = Field(..., description="Balance in trade")
    currencies: Dict[str, float] = Field(..., description="Balance by currency")

class PositionResponse(BaseModel):
    """
    Position response model.
    """
    
    symbol: str = Field(..., description="Trading pair symbol")
    amount: float = Field(..., description="Position amount")
    entry_price: float = Field(..., description="Entry price")
    current_price: float = Field(..., description="Current price")
    stop_loss: float = Field(..., description="Stop loss price")
    take_profit: float = Field(..., description="Take profit price")
    profit_loss: float = Field(..., description="Profit/loss")
    profit_loss_percentage: float = Field(..., description="Profit/loss percentage")

class ConfigUpdateRequest(BaseModel):
    """
    Configuration update request model.
    """
    
    trading_pairs: Optional[List[str]] = Field(None, description="Trading pairs")
    risk_percentage: Optional[float] = Field(None, description="Risk percentage")
    max_position_size: Optional[float] = Field(None, description="Maximum position size")
    stop_loss_percentage: Optional[float] = Field(None, description="Stop loss percentage")
    take_profit_percentage: Optional[float] = Field(None, description="Take profit percentage")
    short_ma_period: Optional[int] = Field(None, description="Short MA period")
    long_ma_period: Optional[int] = Field(None, description="Long MA period")
    rsi_period: Optional[int] = Field(None, description="RSI period")
    rsi_buy_threshold: Optional[float] = Field(None, description="RSI buy threshold")
    rsi_sell_threshold: Optional[float] = Field(None, description="RSI sell threshold")

class TradeRequest(BaseModel):
    """
    Trade request model.
    """
    
    symbol: str = Field(..., description="Trading pair symbol")
    type: str = Field(..., description="Trade type ('buy' or 'sell')")
    amount: float = Field(..., description="Trade amount")
    price: Optional[float] = Field(None, description="Trade price (for limit orders)")

class BacktestRequest(BaseModel):
    """
    Backtest request model.
    """
    
    symbol: str = Field(..., description="Trading pair symbol")
    start_date: str = Field(..., description="Start date (ISO format)")
    end_date: str = Field(..., description="End date (ISO format)")
    timeframe: str = Field("15m", description="Timeframe")
    initial_balance: float = Field(100.0, description="Initial balance")

class BacktestResponse(BaseModel):
    """
    Backtest response model.
    """
    
    symbol: str = Field(..., description="Trading pair symbol")
    start_date: str = Field(..., description="Start date")
    end_date: str = Field(..., description="End date")
    timeframe: str = Field(..., description="Timeframe")
    initial_balance: float = Field(..., description="Initial balance")
    final_balance: float = Field(..., description="Final balance")
    profit_loss: float = Field(..., description="Profit/loss")
    profit_loss_percentage: float = Field(..., description="Profit/loss percentage")
    trades: List[TradeResponse] = Field(..., description="Trades")
