#!/usr/bin/env python3
"""
Backtest script for the trading bot.

This script runs a backtest of the trading bot's strategy on historical data.
"""

import asyncio
import argparse
import json
from datetime import datetime, timedelta
import logging

from app.config import get_config, validate_config
from app.bot import TradingBot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

async def run_backtest(
    symbol: str,
    start_date: str,
    end_date: str,
    timeframe: str = "15m",
    initial_balance: float = 100.0,
    output_file: str = None,
):
    """
    Run a backtest.
    
    Args:
        symbol (str): Trading pair symbol (e.g., 'BTC/USDT').
        start_date (str): Start date (ISO format).
        end_date (str): End date (ISO format).
        timeframe (str, optional): Timeframe. Defaults to "15m".
        initial_balance (float, optional): Initial balance. Defaults to 100.0.
        output_file (str, optional): Output file path. Defaults to None.
    """
    # Validate configuration
    if not validate_config():
        logger.error("Bot is not properly configured. Check the logs for details.")
        return
    
    # Get configuration
    config = get_config()
    
    # Create bot instance
    bot = TradingBot(config)
    
    # Run the backtest
    logger.info(f"Running backtest for {symbol} from {start_date} to {end_date}")
    result = await bot.backtest(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        timeframe=timeframe,
        initial_balance=initial_balance,
    )
    
    # Print the result
    logger.info(f"Backtest completed: Balance: ${result['final_balance']:.2f}, "
               f"P/L: ${result['profit_loss']:.2f} ({result['profit_loss_percentage']:.2f}%)")
    
    # Print trades
    logger.info(f"Trades: {len(result['trades'])}")
    for trade in result['trades']:
        logger.info(f"{trade['timestamp']} - {trade['type'].upper()} {trade['amount']} {symbol} at ${trade['price']:.2f}")
    
    # Save the result to a file
    if output_file:
        with open(output_file, "w") as f:
            json.dump(result, f, indent=2)
        logger.info(f"Backtest result saved to {output_file}")

def parse_args():
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Run a backtest of the trading bot's strategy.")
    
    parser.add_argument(
        "--symbol",
        type=str,
        default="BTC/USDT",
        help="Trading pair symbol (e.g., 'BTC/USDT').",
    )
    
    parser.add_argument(
        "--start-date",
        type=str,
        default=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
        help="Start date (ISO format).",
    )
    
    parser.add_argument(
        "--end-date",
        type=str,
        default=datetime.now().strftime("%Y-%m-%d"),
        help="End date (ISO format).",
    )
    
    parser.add_argument(
        "--timeframe",
        type=str,
        default="15m",
        help="Timeframe.",
    )
    
    parser.add_argument(
        "--initial-balance",
        type=float,
        default=100.0,
        help="Initial balance.",
    )
    
    parser.add_argument(
        "--output-file",
        type=str,
        default=None,
        help="Output file path.",
    )
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    
    asyncio.run(run_backtest(
        symbol=args.symbol,
        start_date=args.start_date,
        end_date=args.end_date,
        timeframe=args.timeframe,
        initial_balance=args.initial_balance,
        output_file=args.output_file,
    ))
