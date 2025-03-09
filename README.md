# Binance Spot Trading Bot

A Python-based trading bot for Binance spot trading using a Moving Average Crossover strategy with RSI confirmation.

## Strategy Overview

This bot implements a trend-following strategy with the following rules:

- **BUY when**:
  - Short MA (20-period) crosses above Long MA (50-period) → Uptrend signal
  - RSI is between 30-50 (not overbought)
  
- **SELL when**:
  - Short MA crosses below Long MA → Downtrend signal
  - RSI is above 70 (overbought, possible reversal)

## Features

- Real-time data collection from Binance
- Technical indicator calculation (Moving Averages, RSI)
- Automated trade execution
- Risk management with stop-loss and take-profit
- Telegram notifications for trade alerts
- FastAPI interface for monitoring and control
- Backtesting capabilities
- Kubernetes deployment support

## Trading Pairs

The bot is configured to trade the following pairs:
- BTC/USDT
- ETH/USDT
- XRP/USDT
- ADA/USDT
- SOL/USDT

## Prerequisites

- Python 3.9 or higher
- Binance account with API keys
- Telegram bot token (optional, for notifications)
- Docker (for containerization)
- Kubernetes cluster (for production deployment)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/binance-trading-bot.git
   cd binance-trading-bot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure your `.env` file with your Binance API keys and Telegram bot token:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

## Configuration

All configuration is stored in the `.env` file. The main configuration parameters are:

- `BINANCE_API_KEY` and `BINANCE_API_SECRET`: Your Binance API credentials
- `TRADING_PAIRS`: Comma-separated list of trading pairs
- `INVESTMENT_AMOUNT`: Total investment amount in USDT
- `RISK_PERCENTAGE`: Percentage of investment to risk
- `MAX_POSITION_SIZE`: Maximum position size per trade
- `STOP_LOSS_PERCENTAGE`: Stop loss percentage
- `TAKE_PROFIT_PERCENTAGE`: Take profit percentage
- `SHORT_MA_PERIOD`, `LONG_MA_PERIOD`, `RSI_PERIOD`: Technical indicator parameters
- `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`: Telegram notification settings

## Usage

### Running the Bot Locally

You can run the bot in several ways:

1. **Using the FastAPI interface**:
   ```bash
   python -m app.main
   ```
   This will start the FastAPI server on http://0.0.0.0:8000

2. **Running the bot directly**:
   ```bash
   ./run_bot.py
   ```
   or
   ```bash
   python run_bot.py
   ```

3. **Running the bot as a module**:
   ```bash
   python -m app.main bot
   ```

### API Endpoints

The bot provides a FastAPI interface with the following endpoints:

- `GET /api/status` - Get the current status of the bot
- `GET /api/trades` - Get the history of trades
- `GET /api/balance` - Get the current balance
- `GET /api/positions` - Get the current positions
- `POST /api/trade` - Create a manual trade
- `POST /start` - Start the bot
- `POST /stop` - Stop the bot
- `POST /api/config` - Update the bot configuration
- `POST /api/backtest` - Run a backtest

### Backtesting

You can run a backtest to evaluate the strategy's performance on historical data:

```bash
./backtest.py --symbol BTC/USDT --start-date 2023-01-01 --end-date 2023-02-01 --initial-balance 100 --output-file backtest_results.json
```

Available options:
- `--symbol`: Trading pair symbol (default: BTC/USDT)
- `--start-date`: Start date in ISO format (default: 30 days ago)
- `--end-date`: End date in ISO format (default: today)
- `--timeframe`: Timeframe (default: 15m)
- `--initial-balance`: Initial balance in USDT (default: 100)
- `--output-file`: Output file path for results (optional)

## Deployment

### Docker

You can build and run the bot using Docker:

```bash
# Build the Docker image
docker build -t moriluz88/trading-bot:latest .

# Run the Docker container
docker run -p 8000:8000 --env-file .env moriluz88/trading-bot:latest
```

Or use the provided script:

```bash
./build-and-push.sh
```

### Kubernetes

To deploy the bot to a Kubernetes cluster:

1. Update the Kubernetes manifests in the `k8s/` directory as needed.
2. Update the secrets in `k8s/secrets.yaml` with your Binance API keys and Telegram bot token.
3. Deploy the application:

```bash
./deploy.sh
```

This will:
- Create a namespace for the bot
- Apply all Kubernetes manifests
- Wait for the deployment to be ready

To access the API:

```bash
kubectl -n trading-bot port-forward svc/trading-bot 8000:8000
```

Then open http://localhost:8000 in your browser.

## VPS Options for Production

For running the bot in production, you can use a VPS (Virtual Private Server). Here are some affordable options:

1. **DigitalOcean**
   - Basic Droplet: $5/month (1GB RAM, 1 vCPU)
   - Standard Droplet: $10/month (2GB RAM, 1 vCPU)

2. **Linode**
   - Nanode: $5/month (1GB RAM, 1 vCPU)
   - Linode 2GB: $10/month (2GB RAM, 1 vCPU)

3. **Vultr**
   - Cloud Compute: $5/month (1GB RAM, 1 vCPU)

4. **Hetzner Cloud**
   - CX11: €3.49/month (2GB RAM, 1 vCPU)

For Kubernetes, you can use:

1. **DigitalOcean Kubernetes**
   - Starting at $10/month plus node costs

2. **Linode Kubernetes Engine (LKE)**
   - Starting at $10/month plus node costs

3. **Civo**
   - K3s cluster starting at $5/month per node

For the trading bot, a small VPS with 1-2GB RAM should be sufficient.

## Project Structure

```
binance-trading-bot/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI entry point
│   ├── bot.py                  # Main bot class
│   ├── config.py               # Configuration
│   ├── data/                   # Data collection
│   ├── strategy/               # Trading strategies
│   ├── execution/              # Order execution
│   ├── risk/                   # Risk management
│   ├── notification/           # Notifications
│   └── api/                    # API endpoints
├── k8s/                        # Kubernetes manifests
├── backtest.py                 # Backtesting script
├── run_bot.py                  # Bot runner script
├── build-and-push.sh           # Docker build script
├── deploy.sh                   # Kubernetes deployment script
├── Dockerfile                  # Docker configuration
├── requirements.txt            # Dependencies
├── .env                        # Environment variables
└── README.md                   # Documentation
```

## Security Considerations

- Never share your API keys or .env file
- Use API keys with trading permissions only (not withdrawal)
- Start with a small investment amount to test the bot
- Monitor the bot regularly
- When using Kubernetes, store secrets securely
- Consider using a secrets management solution for production

## Disclaimer

This trading bot is for educational purposes only. Use at your own risk. The authors are not responsible for any financial losses incurred from using this software. Cryptocurrency trading involves significant risk and you should only invest what you can afford to lose.
