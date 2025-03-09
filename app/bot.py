"""
Bot module for the trading bot.

This module provides the main bot class that ties everything together.
"""

import logging
import asyncio
import time
from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime

from app.config import get_config
from app.data.collector import BinanceDataCollector
from app.data.indicators import TechnicalIndicators
from app.strategy.ma_crossover import MACrossoverStrategy
from app.execution.binance import BinanceAPI
from app.execution.order import OrderManager
from app.risk.manager import RiskManager
from app.notification.telegram import create_telegram_notifier

logger = logging.getLogger(__name__)

class TradingBot:
    """
    Trading bot.
    
    This class is the main entry point for the trading bot.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the trading bot.
        
        Args:
            config (Dict[str, Any]): Configuration dictionary.
        """
        self.config = config
        self.is_running = False
        self.stop_event = asyncio.Event()
        
        # Initialize components
        self.data_collector = BinanceDataCollector(
            api_key=config["binance"]["api_key"],
            api_secret=config["binance"]["api_secret"],
        )
        
        self.strategy = MACrossoverStrategy(config)
        
        self.binance_api = BinanceAPI(
            api_key=config["binance"]["api_key"],
            api_secret=config["binance"]["api_secret"],
        )
        
        self.order_manager = OrderManager(
            binance_api=self.binance_api,
            config=config,
        )
        
        self.risk_manager = RiskManager(config)
        
        self.telegram_notifier = create_telegram_notifier(config)
        
        logger.info("Trading bot initialized")
    
    async def run(self):
        """
        Run the trading bot.
        """
        try:
            self.is_running = True
            logger.info("Starting the trading bot...")
            
            if self.telegram_notifier:
                await self.telegram_notifier.send_status_notification("Bot started")
            
            # Main loop
            while not self.stop_event.is_set():
                try:
                    # Get trading pairs from config
                    trading_pairs = self.config["trading"]["pairs"]
                    
                    # Collect data for each trading pair
                    data = {}
                    for symbol in trading_pairs:
                        # Get historical data
                        df = self.data_collector.get_historical_data(
                            symbol=symbol,
                            timeframe=self.config["trading"]["timeframe"],
                            limit=100,
                        )
                        
                        # Add technical indicators
                        df_with_indicators = TechnicalIndicators.add_indicators(df, self.config)
                        
                        # Store data
                        data[symbol] = df_with_indicators
                    
                    # Generate signals
                    signals = self.strategy.generate_signals(data)
                    
                    # Process signals
                    for symbol, signal in signals.items():
                        current_price = data[symbol].iloc[-1]["close"]
                        
                        # Check if we have a position for this symbol
                        position = self.risk_manager.get_position(symbol)
                        
                        if signal == 1 and position is None:
                            # Buy signal and no position
                            amount = self.risk_manager.calculate_position_size(symbol, current_price)
                            
                            # Create buy order
                            order = self.order_manager.create_buy_order(symbol, amount)
                            
                            # Add position
                            self.risk_manager.add_position(symbol, amount, current_price)
                            
                            # Send notification
                            if self.telegram_notifier:
                                indicators = {
                                    "MA(20)": data[symbol].iloc[-1][f"ma_{self.config['indicators']['short_ma_period']}"],
                                    "MA(50)": data[symbol].iloc[-1][f"ma_{self.config['indicators']['long_ma_period']}"],
                                    "RSI": data[symbol].iloc[-1]["rsi"],
                                }
                                await self.telegram_notifier.send_signal_notification("buy", symbol, current_price, indicators)
                                await self.telegram_notifier.send_trade_notification("buy", symbol, amount, current_price)
                        
                        elif signal == -1 and position is not None:
                            # Sell signal and have position
                            amount = position["amount"]
                            
                            # Create sell order
                            order = self.order_manager.create_sell_order(symbol, amount)
                            
                            # Remove position
                            self.risk_manager.remove_position(symbol)
                            
                            # Send notification
                            if self.telegram_notifier:
                                indicators = {
                                    "MA(20)": data[symbol].iloc[-1][f"ma_{self.config['indicators']['short_ma_period']}"],
                                    "MA(50)": data[symbol].iloc[-1][f"ma_{self.config['indicators']['long_ma_period']}"],
                                    "RSI": data[symbol].iloc[-1]["rsi"],
                                }
                                await self.telegram_notifier.send_signal_notification("sell", symbol, current_price, indicators)
                                await self.telegram_notifier.send_trade_notification("sell", symbol, amount, current_price)
                        
                        elif position is not None:
                            # Update position
                            self.risk_manager.update_position(symbol, current_price)
                            
                            # Check stop loss and take profit
                            if self.risk_manager.check_stop_loss(symbol, current_price):
                                # Stop loss triggered
                                amount = position["amount"]
                                
                                # Create sell order
                                order = self.order_manager.create_sell_order(symbol, amount)
                                
                                # Remove position
                                self.risk_manager.remove_position(symbol)
                                
                                # Send notification
                                if self.telegram_notifier:
                                    await self.telegram_notifier.send_status_notification(f"Stop loss triggered for {symbol} at {current_price:.2f}")
                                    await self.telegram_notifier.send_trade_notification("sell", symbol, amount, current_price)
                            
                            elif self.risk_manager.check_take_profit(symbol, current_price):
                                # Take profit triggered
                                amount = position["amount"]
                                
                                # Create sell order
                                order = self.order_manager.create_sell_order(symbol, amount)
                                
                                # Remove position
                                self.risk_manager.remove_position(symbol)
                                
                                # Send notification
                                if self.telegram_notifier:
                                    await self.telegram_notifier.send_status_notification(f"Take profit triggered for {symbol} at {current_price:.2f}")
                                    await self.telegram_notifier.send_trade_notification("sell", symbol, amount, current_price)
                    
                    # Sleep for a while
                    await asyncio.sleep(60)  # Sleep for 1 minute
                
                except Exception as e:
                    logger.exception(f"Error in main loop: {e}")
                    if self.telegram_notifier:
                        await self.telegram_notifier.send_error_notification(f"Error in main loop: {e}")
                    
                    # Sleep for a while before retrying
                    await asyncio.sleep(60)  # Sleep for 1 minute
            
            logger.info("Trading bot stopped")
            if self.telegram_notifier:
                await self.telegram_notifier.send_status_notification("Bot stopped")
        
        except Exception as e:
            logger.exception(f"Error running trading bot: {e}")
            if self.telegram_notifier:
                await self.telegram_notifier.send_error_notification(f"Error running trading bot: {e}")
        
        finally:
            self.is_running = False
    
    def stop(self):
        """
        Stop the trading bot.
        """
        logger.info("Stopping the trading bot...")
        self.stop_event.set()
    
    async def backtest(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        timeframe: str = "15m",
        initial_balance: float = 100.0,
    ) -> Dict[str, Any]:
        """
        Run a backtest.
        
        Args:
            symbol (str): Trading pair symbol (e.g., 'BTC/USDT').
            start_date (str): Start date (ISO format).
            end_date (str): End date (ISO format).
            timeframe (str, optional): Timeframe. Defaults to "15m".
            initial_balance (float, optional): Initial balance. Defaults to 100.0.
        
        Returns:
            Dict[str, Any]: Backtest results.
        """
        try:
            logger.info(f"Running backtest for {symbol} from {start_date} to {end_date}")
            
            # Convert dates to timestamps
            start_timestamp = int(datetime.fromisoformat(start_date).timestamp() * 1000)
            end_timestamp = int(datetime.fromisoformat(end_date).timestamp() * 1000)
            
            # Get historical data
            df = self.data_collector.get_historical_data(
                symbol=symbol,
                timeframe=timeframe,
                since=start_timestamp,
            )
            
            # Filter data by date
            df = df[start_date:end_date]
            
            # Add technical indicators
            df_with_indicators = TechnicalIndicators.add_indicators(df, self.config)
            
            # Initialize backtest variables
            balance = initial_balance
            position = None
            trades = []
            
            # Run backtest
            for i in range(1, len(df_with_indicators)):
                # Get current row
                row = df_with_indicators.iloc[i]
                prev_row = df_with_indicators.iloc[i-1]
                
                # Get current price
                current_price = row["close"]
                
                # Check for buy signal
                if (prev_row[f"ma_{self.config['indicators']['short_ma_period']}"] <= prev_row[f"ma_{self.config['indicators']['long_ma_period']}"] and
                    row[f"ma_{self.config['indicators']['short_ma_period']}"] > row[f"ma_{self.config['indicators']['long_ma_period']}"]) and \
                   (row["rsi"] >= 30 and row["rsi"] <= 50) and \
                   position is None:
                    # Buy signal
                    amount = (balance * 0.95) / current_price  # Use 95% of balance
                    cost = amount * current_price
                    balance -= cost
                    
                    # Create position
                    position = {
                        "symbol": symbol,
                        "amount": amount,
                        "entry_price": current_price,
                        "timestamp": row.name.isoformat(),
                    }
                    
                    # Add trade
                    trades.append({
                        "id": str(len(trades) + 1),
                        "symbol": symbol,
                        "type": "buy",
                        "price": current_price,
                        "amount": amount,
                        "timestamp": row.name.isoformat(),
                        "status": "completed",
                    })
                
                # Check for sell signal
                elif ((prev_row[f"ma_{self.config['indicators']['short_ma_period']}"] >= prev_row[f"ma_{self.config['indicators']['long_ma_period']}"] and
                       row[f"ma_{self.config['indicators']['short_ma_period']}"] < row[f"ma_{self.config['indicators']['long_ma_period']}"]) or \
                      row["rsi"] >= 70) and \
                     position is not None:
                    # Sell signal
                    amount = position["amount"]
                    revenue = amount * current_price
                    balance += revenue
                    
                    # Add trade
                    trades.append({
                        "id": str(len(trades) + 1),
                        "symbol": symbol,
                        "type": "sell",
                        "price": current_price,
                        "amount": amount,
                        "timestamp": row.name.isoformat(),
                        "status": "completed",
                    })
                    
                    # Clear position
                    position = None
                
                # Check for stop loss
                elif position is not None and current_price <= position["entry_price"] * (1 - self.config["trading"]["stop_loss_percentage"] / 100):
                    # Stop loss triggered
                    amount = position["amount"]
                    revenue = amount * current_price
                    balance += revenue
                    
                    # Add trade
                    trades.append({
                        "id": str(len(trades) + 1),
                        "symbol": symbol,
                        "type": "sell",
                        "price": current_price,
                        "amount": amount,
                        "timestamp": row.name.isoformat(),
                        "status": "completed",
                    })
                    
                    # Clear position
                    position = None
                
                # Check for take profit
                elif position is not None and current_price >= position["entry_price"] * (1 + self.config["trading"]["take_profit_percentage"] / 100):
                    # Take profit triggered
                    amount = position["amount"]
                    revenue = amount * current_price
                    balance += revenue
                    
                    # Add trade
                    trades.append({
                        "id": str(len(trades) + 1),
                        "symbol": symbol,
                        "type": "sell",
                        "price": current_price,
                        "amount": amount,
                        "timestamp": row.name.isoformat(),
                        "status": "completed",
                    })
                    
                    # Clear position
                    position = None
            
            # Sell any remaining position at the last price
            if position is not None:
                amount = position["amount"]
                last_price = df_with_indicators.iloc[-1]["close"]
                revenue = amount * last_price
                balance += revenue
                
                # Add trade
                trades.append({
                    "id": str(len(trades) + 1),
                    "symbol": symbol,
                    "type": "sell",
                    "price": last_price,
                    "amount": amount,
                    "timestamp": df_with_indicators.index[-1].isoformat(),
                    "status": "completed",
                })
            
            # Calculate profit/loss
            profit_loss = balance - initial_balance
            profit_loss_percentage = (profit_loss / initial_balance) * 100
            
            logger.info(f"Backtest completed: Balance: ${balance:.2f}, P/L: ${profit_loss:.2f} ({profit_loss_percentage:.2f}%)")
            
            return {
                "symbol": symbol,
                "start_date": start_date,
                "end_date": end_date,
                "timeframe": timeframe,
                "initial_balance": initial_balance,
                "final_balance": balance,
                "profit_loss": profit_loss,
                "profit_loss_percentage": profit_loss_percentage,
                "trades": trades,
            }
        
        except Exception as e:
            logger.exception(f"Error running backtest: {e}")
            raise
