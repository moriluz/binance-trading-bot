"""
API routes module for the trading bot.

This module provides the FastAPI routes for the API.
"""

import logging
import asyncio
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Dict, Any, Optional

from app.api.models import (
    StatusResponse,
    TradeResponse,
    BalanceResponse,
    PositionResponse,
    ConfigUpdateRequest,
    TradeRequest,
    BacktestRequest,
    BacktestResponse,
)
from app.config import get_config, validate_config
from app.bot import TradingBot

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Global variables
bot_instance = None

# Dependency to check if the bot is configured
async def check_config():
    if not validate_config():
        raise HTTPException(
            status_code=500,
            detail="Bot is not properly configured. Check the logs for details.",
        )
    return get_config()

# Dependency to check if the bot is running
async def check_bot_running():
    from app.main import bot_instance
    
    if bot_instance is None or not bot_instance.is_running:
        raise HTTPException(
            status_code=400,
            detail="Bot is not running. Start the bot first.",
        )
    return bot_instance

# Routes
@router.get("/", response_model=Dict[str, str])
async def root():
    """
    Root endpoint.
    
    Returns:
        Dict[str, str]: Welcome message.
    """
    return {"message": "Welcome to the Binance Trading Bot API"}

@router.get("/status", response_model=StatusResponse)
async def get_status(config: Dict[str, Any] = Depends(check_config)):
    """
    Get the current status of the bot.
    
    Args:
        config (Dict[str, Any]): Bot configuration.
    
    Returns:
        StatusResponse: Bot status.
    """
    from app.main import bot_instance
    
    is_running = bot_instance is not None and bot_instance.is_running
    
    return {
        "status": "running" if is_running else "stopped",
        "running": is_running,
        "config": config,
    }

@router.get("/trades", response_model=List[TradeResponse])
async def get_trades(
    bot = Depends(check_bot_running),
    config: Dict[str, Any] = Depends(check_config),
):
    """
    Get the history of trades.
    
    Args:
        bot: Bot instance.
        config (Dict[str, Any]): Bot configuration.
    
    Returns:
        List[TradeResponse]: Trade history.
    """
    # Get trades from the order manager
    trades = bot.order_manager.get_all_orders()
    
    # Convert to TradeResponse format
    trade_responses = []
    for trade in trades:
        trade_responses.append({
            "id": trade["id"],
            "symbol": trade["symbol"],
            "type": trade["type"],
            "price": trade["price"],
            "amount": trade["amount"],
            "timestamp": trade["timestamp"],
            "status": trade["status"],
        })
    
    return trade_responses

@router.get("/balance", response_model=BalanceResponse)
async def get_balance(
    bot = Depends(check_bot_running),
    config: Dict[str, Any] = Depends(check_config),
):
    """
    Get the current balance.
    
    Args:
        bot: Bot instance.
        config (Dict[str, Any]): Bot configuration.
    
    Returns:
        BalanceResponse: Current balance.
    """
    try:
        # Get balance from Binance
        balance = bot.binance_api.get_balance()
        
        # Calculate total balance
        total_balance = 0.0
        available_balance = 0.0
        in_trade = 0.0
        currencies = {}
        
        # Process balance data
        for currency, data in balance["total"].items():
            if isinstance(data, (int, float)) and data > 0:
                currencies[currency] = data
                
                # Get current price if not USDT
                if currency != "USDT":
                    try:
                        ticker = bot.binance_api.get_ticker(f"{currency}/USDT")
                        price = ticker["last"]
                        total_balance += data * price
                    except:
                        # Skip if we can't get the price
                        pass
                else:
                    total_balance += data
        
        # Calculate in_trade balance
        positions = bot.risk_manager.get_all_positions()
        for position in positions:
            in_trade += position["amount"] * position["current_price"]
        
        # Calculate available balance
        available_balance = total_balance - in_trade
        
        return {
            "total_balance": total_balance,
            "available_balance": available_balance,
            "in_trade": in_trade,
            "currencies": currencies,
        }
    except Exception as e:
        logger.exception(f"Error getting balance: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting balance: {str(e)}",
        )

@router.get("/positions", response_model=List[PositionResponse])
async def get_positions(
    bot = Depends(check_bot_running),
    config: Dict[str, Any] = Depends(check_config),
):
    """
    Get the current positions.
    
    Args:
        bot: Bot instance.
        config (Dict[str, Any]): Bot configuration.
    
    Returns:
        List[PositionResponse]: Current positions.
    """
    # Get positions from the risk manager
    positions = bot.risk_manager.get_all_positions()
    
    # Convert to PositionResponse format
    position_responses = []
    for position in positions:
        position_responses.append({
            "symbol": position["symbol"],
            "amount": position["amount"],
            "entry_price": position["entry_price"],
            "current_price": position["current_price"],
            "stop_loss": position["stop_loss"],
            "take_profit": position["take_profit"],
            "profit_loss": position["profit_loss"],
            "profit_loss_percentage": position["profit_loss_percentage"],
        })
    
    return position_responses

@router.post("/trade", response_model=TradeResponse)
async def create_trade(
    trade_request: TradeRequest,
    bot = Depends(check_bot_running),
    config: Dict[str, Any] = Depends(check_config),
):
    """
    Create a trade.
    
    Args:
        trade_request (TradeRequest): Trade request.
        bot: Bot instance.
        config (Dict[str, Any]): Bot configuration.
    
    Returns:
        TradeResponse: Trade response.
    """
    try:
        # Create the trade
        if trade_request.type.lower() == "buy":
            order = bot.order_manager.create_buy_order(
                symbol=trade_request.symbol,
                amount=trade_request.amount,
                price=trade_request.price,
            )
        elif trade_request.type.lower() == "sell":
            order = bot.order_manager.create_sell_order(
                symbol=trade_request.symbol,
                amount=trade_request.amount,
                price=trade_request.price,
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid trade type: {trade_request.type}",
            )
        
        # Return the trade response
        return {
            "id": order["id"],
            "symbol": order["symbol"],
            "type": order["type"],
            "price": order["price"],
            "amount": order["amount"],
            "timestamp": order["timestamp"],
            "status": order["status"],
        }
    except Exception as e:
        logger.exception(f"Error creating trade: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error creating trade: {str(e)}",
        )

@router.post("/backtest", response_model=BacktestResponse)
async def run_backtest(
    backtest_request: BacktestRequest,
    config: Dict[str, Any] = Depends(check_config),
):
    """
    Run a backtest.
    
    Args:
        backtest_request (BacktestRequest): Backtest request.
        config (Dict[str, Any]): Bot configuration.
    
    Returns:
        BacktestResponse: Backtest response.
    """
    try:
        # Create a bot instance for backtesting
        bot = TradingBot(config)
        
        # Run the backtest
        result = await bot.backtest(
            symbol=backtest_request.symbol,
            start_date=backtest_request.start_date,
            end_date=backtest_request.end_date,
            timeframe=backtest_request.timeframe,
            initial_balance=backtest_request.initial_balance,
        )
        
        return result
    except Exception as e:
        logger.exception(f"Error running backtest: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error running backtest: {str(e)}",
        )

@router.post("/config", response_model=Dict[str, str])
async def update_config(
    config_update: ConfigUpdateRequest,
    config: Dict[str, Any] = Depends(check_config),
):
    """
    Update the bot configuration.
    
    Args:
        config_update (ConfigUpdateRequest): Configuration update.
        config (Dict[str, Any]): Current configuration.
    
    Returns:
        Dict[str, str]: Success message.
    """
    try:
        # Update configuration
        if config_update.trading_pairs is not None:
            config["trading"]["pairs"] = config_update.trading_pairs
        
        if config_update.risk_percentage is not None:
            config["trading"]["risk_percentage"] = config_update.risk_percentage
        
        if config_update.max_position_size is not None:
            config["trading"]["max_position_size"] = config_update.max_position_size
        
        if config_update.stop_loss_percentage is not None:
            config["trading"]["stop_loss_percentage"] = config_update.stop_loss_percentage
        
        if config_update.take_profit_percentage is not None:
            config["trading"]["take_profit_percentage"] = config_update.take_profit_percentage
        
        if config_update.short_ma_period is not None:
            config["indicators"]["short_ma_period"] = config_update.short_ma_period
        
        if config_update.long_ma_period is not None:
            config["indicators"]["long_ma_period"] = config_update.long_ma_period
        
        if config_update.rsi_period is not None:
            config["indicators"]["rsi_period"] = config_update.rsi_period
        
        if config_update.rsi_buy_threshold is not None:
            config["indicators"]["rsi_buy_threshold"] = config_update.rsi_buy_threshold
        
        if config_update.rsi_sell_threshold is not None:
            config["indicators"]["rsi_sell_threshold"] = config_update.rsi_sell_threshold
        
        # If the bot is running, update its configuration
        from app.main import bot_instance
        if bot_instance is not None and bot_instance.is_running:
            bot_instance.config = config
        
        return {"message": "Configuration updated successfully"}
    except Exception as e:
        logger.exception(f"Error updating configuration: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error updating configuration: {str(e)}",
        )
