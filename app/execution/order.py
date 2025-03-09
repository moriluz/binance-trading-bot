"""
Order management module for the trading bot.

This module provides a class for managing orders.
"""

import logging
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime

from app.execution.binance import BinanceAPI

logger = logging.getLogger(__name__)

class OrderManager:
    """
    Order manager.
    
    This class is responsible for managing orders.
    """
    
    def __init__(self, binance_api: BinanceAPI, config: Dict[str, Any]):
        """
        Initialize the order manager.
        
        Args:
            binance_api (BinanceAPI): Binance API wrapper.
            config (Dict[str, Any]): Configuration dictionary.
        """
        self.binance_api = binance_api
        self.config = config
        self.orders = {}  # Dictionary to store orders
        
        logger.info("Order manager initialized")
    
    def create_buy_order(self, symbol: str, amount: float, price: Optional[float] = None) -> Dict[str, Any]:
        """
        Create a buy order.
        
        Args:
            symbol (str): Trading pair symbol (e.g., 'BTC/USDT').
            amount (float): Amount to buy.
            price (float, optional): Price to buy at. Defaults to None (market order).
        
        Returns:
            Dict[str, Any]: Order data.
        """
        try:
            # Generate a unique order ID
            order_id = str(uuid.uuid4())
            
            # Create the order
            if price is None:
                # Market order
                order = self.binance_api.create_market_buy_order(symbol, amount)
            else:
                # Limit order
                order = self.binance_api.create_limit_buy_order(symbol, amount, price)
            
            # Store the order
            self.orders[order_id] = {
                "id": order_id,
                "exchange_id": order["id"],
                "symbol": symbol,
                "type": "buy",
                "amount": amount,
                "price": price if price is not None else order["price"],
                "status": order["status"],
                "timestamp": datetime.now().isoformat(),
            }
            
            logger.info(f"Created buy order {order_id} for {amount} {symbol}")
            
            return self.orders[order_id]
        except Exception as e:
            logger.exception(f"Error creating buy order: {e}")
            raise
    
    def create_sell_order(self, symbol: str, amount: float, price: Optional[float] = None) -> Dict[str, Any]:
        """
        Create a sell order.
        
        Args:
            symbol (str): Trading pair symbol (e.g., 'BTC/USDT').
            amount (float): Amount to sell.
            price (float, optional): Price to sell at. Defaults to None (market order).
        
        Returns:
            Dict[str, Any]: Order data.
        """
        try:
            # Generate a unique order ID
            order_id = str(uuid.uuid4())
            
            # Create the order
            if price is None:
                # Market order
                order = self.binance_api.create_market_sell_order(symbol, amount)
            else:
                # Limit order
                order = self.binance_api.create_limit_sell_order(symbol, amount, price)
            
            # Store the order
            self.orders[order_id] = {
                "id": order_id,
                "exchange_id": order["id"],
                "symbol": symbol,
                "type": "sell",
                "amount": amount,
                "price": price if price is not None else order["price"],
                "status": order["status"],
                "timestamp": datetime.now().isoformat(),
            }
            
            logger.info(f"Created sell order {order_id} for {amount} {symbol}")
            
            return self.orders[order_id]
        except Exception as e:
            logger.exception(f"Error creating sell order: {e}")
            raise
    
    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """
        Cancel an order.
        
        Args:
            order_id (str): Order ID.
        
        Returns:
            Dict[str, Any]: Order data.
        """
        try:
            # Get the order
            order = self.orders.get(order_id)
            if order is None:
                raise ValueError(f"Order {order_id} not found")
            
            # Cancel the order
            self.binance_api.cancel_order(order["exchange_id"], order["symbol"])
            
            # Update the order status
            order["status"] = "canceled"
            
            logger.info(f"Cancelled order {order_id}")
            
            return order
        except Exception as e:
            logger.exception(f"Error cancelling order: {e}")
            raise
    
    def get_order(self, order_id: str) -> Dict[str, Any]:
        """
        Get an order.
        
        Args:
            order_id (str): Order ID.
        
        Returns:
            Dict[str, Any]: Order data.
        """
        try:
            # Get the order
            order = self.orders.get(order_id)
            if order is None:
                raise ValueError(f"Order {order_id} not found")
            
            # Get the order from Binance
            binance_order = self.binance_api.get_order(order["exchange_id"], order["symbol"])
            
            # Update the order status
            order["status"] = binance_order["status"]
            
            logger.info(f"Fetched order {order_id}")
            
            return order
        except Exception as e:
            logger.exception(f"Error fetching order: {e}")
            raise
    
    def get_open_orders(self) -> List[Dict[str, Any]]:
        """
        Get open orders.
        
        Returns:
            List[Dict[str, Any]]: Open orders.
        """
        try:
            # Get open orders from Binance
            binance_orders = self.binance_api.get_open_orders()
            
            # Update the order status
            open_orders = []
            for order_id, order in self.orders.items():
                for binance_order in binance_orders:
                    if order["exchange_id"] == binance_order["id"]:
                        order["status"] = binance_order["status"]
                        if order["status"] in ["open", "new", "partially_filled"]:
                            open_orders.append(order)
            
            logger.info(f"Fetched {len(open_orders)} open orders")
            
            return open_orders
        except Exception as e:
            logger.exception(f"Error fetching open orders: {e}")
            raise
    
    def get_closed_orders(self) -> List[Dict[str, Any]]:
        """
        Get closed orders.
        
        Returns:
            List[Dict[str, Any]]: Closed orders.
        """
        try:
            # Get closed orders
            closed_orders = []
            for order_id, order in self.orders.items():
                if order["status"] in ["closed", "filled", "canceled"]:
                    closed_orders.append(order)
            
            logger.info(f"Fetched {len(closed_orders)} closed orders")
            
            return closed_orders
        except Exception as e:
            logger.exception(f"Error fetching closed orders: {e}")
            raise
    
    def get_all_orders(self) -> List[Dict[str, Any]]:
        """
        Get all orders.
        
        Returns:
            List[Dict[str, Any]]: All orders.
        """
        try:
            # Get all orders
            all_orders = list(self.orders.values())
            
            logger.info(f"Fetched {len(all_orders)} orders")
            
            return all_orders
        except Exception as e:
            logger.exception(f"Error fetching all orders: {e}")
            raise
