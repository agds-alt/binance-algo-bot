"""
Binance Algo Trading Bot - Main Entry Point
Production-ready trading bot with optimized strategy
"""

import asyncio
import sys
import os
import signal
from pathlib import Path
from datetime import datetime, timedelta
import logging
from typing import Optional

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.config import (
    ALLOWED_PAIRS,
    SCALPING_CONFIG,
    RISK_LIMITS,
    BINANCE_TESTNET
)
from modules.data_fetcher import DataFetcher
from modules.bot_state_manager import get_bot_state_manager, Position, Trade
from modules.backtester import (
    optimized_ema_crossover_signals,
    relaxed_ema_crossover_signals,
    stochastic_rsi_strategy
)
import pandas as pd

# Setup logging
# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/trading_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TradingBot:
    """
    Main Trading Bot

    Features:
    - Optimized EMA crossover strategy (5/6 confirmations)
    - Multi-pair scanning
    - Risk management
    - Position tracking
    - State persistence
    """

    def __init__(self, testnet: bool = True):
        """
        Initialize trading bot

        Args:
            testnet: Use testnet (True) or live (False)
        """
        self.testnet = testnet
        self.running = False
        self.state_manager = get_bot_state_manager()
        self.fetcher = DataFetcher(use_testnet=testnet)

        # Bot state
        self.capital = 10000  # Will be loaded from state
        self.positions = []
        self.daily_trades = 0
        self.daily_pnl = 0

        logger.info("=" * 70)
        logger.info("🤖 BINANCE ALGO TRADING BOT")
        logger.info("=" * 70)
        logger.info(f"Mode: {'TESTNET' if testnet else '🔴 LIVE TRADING'}")

        # Display strategy name
        strategy_names = {
            "stochastic_rsi": "Stochastic RSI Mean Reversion (Buy <24, Sell >80)",
            "relaxed_ema": "Relaxed EMA Crossover (4/6 confirmations)",
            "ema_crossover": "Optimized EMA Crossover (5/6 confirmations)"
        }
        strategy_name = strategy_names.get(SCALPING_CONFIG.STRATEGY_TYPE, "Unknown Strategy")
        logger.info(f"Strategy: {strategy_name}")

        logger.info(f"Timeframe: {SCALPING_CONFIG.PRIMARY_TIMEFRAME}")
        logger.info(f"Allowed Pairs: {', '.join(ALLOWED_PAIRS)}")
        logger.info(f"Risk per Trade: {RISK_LIMITS.MAX_RISK_PER_TRADE * 100}%")
        logger.info(f"Max Daily Trades: {RISK_LIMITS.MAX_TRADES_PER_DAY}")
        logger.info("=" * 70)

    async def initialize(self):
        """Initialize bot state"""
        logger.info("📊 Initializing bot state...")

        # Start bot state
        self.state_manager.start_bot(
            pid=os.getpid(),
            mode="testnet" if self.testnet else "live",
            capital=self.capital
        )

        # Load existing positions
        self.positions = self.state_manager.get_positions()

        # Count today's trades
        all_trades = self.state_manager.get_trades()
        today_str = datetime.now().strftime('%Y-%m-%d')
        self.daily_trades = sum(1 for t in all_trades
                               if hasattr(t, 'entry_time') and t.entry_time.startswith(today_str))

        logger.info(f"✅ Bot initialized")
        logger.info(f"   Open Positions: {len(self.positions)}")
        logger.info(f"   Daily Trades: {self.daily_trades}/{RISK_LIMITS.MAX_TRADES_PER_DAY}")

    async def scan_market(self, symbol: str) -> Optional[dict]:
        """
        Scan single pair for trading signals

        Args:
            symbol: Trading pair to scan

        Returns:
            Signal dict or None
        """
        try:
            # Fetch recent data
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=6)

            df = self.fetcher.fetch_klines_sync(
                symbol=symbol,
                interval=SCALPING_CONFIG.PRIMARY_TIMEFRAME,
                start_time=start_time,
                end_time=end_time,
                limit=500
            )

            if df.empty or len(df) < 200:
                return None

            # Calculate indicators
            df = self.fetcher.calculate_indicators(df)

            # Generate signal based on selected strategy
            if SCALPING_CONFIG.STRATEGY_TYPE == "stochastic_rsi":
                signal = stochastic_rsi_strategy(df, debug=True)
            elif SCALPING_CONFIG.STRATEGY_TYPE == "relaxed_ema":
                signal = relaxed_ema_crossover_signals(df, debug=True)
            elif SCALPING_CONFIG.STRATEGY_TYPE == "ema_crossover":
                signal = optimized_ema_crossover_signals(df, debug=True)
            else:
                # Default to relaxed EMA
                signal = relaxed_ema_crossover_signals(df, debug=True)

            # ALWAYS log what's happening
            latest = df.iloc[-1]
            prev = df.iloc[-2]

            # Log current market state based on strategy
            if SCALPING_CONFIG.STRATEGY_TYPE == "stochastic_rsi":
                # Show Stochastic RSI values
                stoch_rsi_val = latest.get('stoch_rsi', 0)
                logger.info(f"📊 Scanning {symbol}: Price=${latest['close']:.2f}, "
                           f"Stoch RSI={stoch_rsi_val:.1f}, RSI={latest['rsi']:.1f}, "
                           f"EMA21={latest['ema_21']:.2f}")
            else:
                # Show EMA values for EMA strategies
                logger.info(f"📊 Scanning {symbol}: Price=${latest['close']:.2f}, "
                           f"EMA8={latest['ema_8']:.2f}, EMA21={latest['ema_21']:.2f}, "
                           f"RSI={latest['rsi']:.1f}")

            if signal:
                signal['symbol'] = symbol
                signal['timestamp'] = df.index[-1]

                # Log with debug info
                if signal.get('has_signal'):
                    logger.info(f"✅ SIGNAL DETECTED on {symbol}: {signal['side']} "
                               f"({signal.get('confirmations', 4)}/6 confirmations)")
                    logger.info(f"   Checks: {signal.get('checks', {})}")
                else:
                    logger.info(f"⚠️  No clear signal on {symbol} - {signal.get('confirmations', 0)}/6 confirmations")
                    logger.info(f"   Reason: {signal.get('reason', 'Unknown')}")
                    logger.info(f"   Checks: {signal.get('checks', {})}")
            else:
                logger.info(f"❌ No EMA crossover on {symbol}")

            return signal

        except Exception as e:
            logger.error(f"❌ Error scanning {symbol}: {e}")
            return None

    async def check_risk_limits(self) -> bool:
        """
        Check if we can take new trades

        Returns:
            True if we can trade, False otherwise
        """
        # Check daily trade limit
        if self.daily_trades >= RISK_LIMITS.MAX_TRADES_PER_DAY:
            logger.warning(f"⚠️ Daily trade limit reached ({self.daily_trades}/{RISK_LIMITS.MAX_TRADES_PER_DAY})")
            return False

        # Check max positions
        if len(self.positions) >= RISK_LIMITS.MAX_CONCURRENT_POSITIONS:
            logger.warning(f"⚠️ Max positions reached ({len(self.positions)}/{RISK_LIMITS.MAX_CONCURRENT_POSITIONS})")
            return False

        # Check daily drawdown
        if self.daily_pnl < -(self.capital * RISK_LIMITS.MAX_DAILY_DRAWDOWN):
            logger.warning(f"⚠️ Daily drawdown limit reached (${self.daily_pnl:.2f})")
            return False

        return True

    def calculate_position_size(self, entry_price: float, stop_loss: float) -> float:
        """
        Calculate position size based on risk

        Args:
            entry_price: Entry price
            stop_loss: Stop loss price

        Returns:
            Position size in base currency
        """
        risk_amount = self.capital * RISK_LIMITS.MAX_RISK_PER_TRADE
        risk_per_unit = abs(entry_price - stop_loss)

        if risk_per_unit == 0:
            return 0

        size = risk_amount / risk_per_unit
        return round(size, 6)

    async def execute_trade(self, signal: dict):
        """
        Execute trade based on signal

        Args:
            signal: Signal dictionary from strategy
        """
        try:
            symbol = signal['symbol']
            side = signal['side']
            entry_price = signal['entry_price']
            stop_loss = signal['stop_loss']
            take_profits = signal['take_profits']

            # Calculate position size
            size = self.calculate_position_size(entry_price, stop_loss)

            if size == 0:
                logger.warning(f"⚠️ Position size too small, skipping {symbol}")
                return

            logger.info(f"\n{'='*70}")
            logger.info(f"🎯 EXECUTING {side} TRADE ON {symbol}")
            logger.info(f"{'='*70}")
            logger.info(f"Entry: ${entry_price:,.2f}")
            logger.info(f"Stop Loss: ${stop_loss:,.2f}")
            logger.info(f"TP1: ${take_profits[0]:,.2f}")
            logger.info(f"TP2: ${take_profits[1]:,.2f}")
            logger.info(f"TP3: ${take_profits[2]:,.2f}")
            logger.info(f"Size: {size}")
            logger.info(f"Risk: ${abs(entry_price - stop_loss) * size:,.2f}")

            # In testnet/simulation mode, we don't place real orders
            # In live mode, you would use Binance API here
            if self.testnet:
                logger.info("📝 TESTNET MODE - Simulating order...")

                # Create position
                position = Position(
                    symbol=symbol,
                    side=side,
                    entry_price=entry_price,
                    current_price=entry_price,  # Initially same as entry
                    size=size,
                    pnl=0.0,  # No P&L yet
                    pnl_percent=0.0,  # No P&L yet
                    stop_loss=stop_loss,
                    take_profits=take_profits,
                    entry_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Convert to string
                )

                # Save position
                self.state_manager.add_position(position)
                self.positions.append(position)
                self.daily_trades += 1

                logger.info(f"✅ Position opened (simulated)")
                logger.info(f"   Total Positions: {len(self.positions)}")
                logger.info(f"   Daily Trades: {self.daily_trades}/{RISK_LIMITS.MAX_TRADES_PER_DAY}")
            else:
                # TODO: Implement live trading with Binance API
                logger.warning("🔴 LIVE TRADING NOT IMPLEMENTED - Use testnet for now")

        except Exception as e:
            logger.error(f"❌ Error executing trade: {e}")
            import traceback
            traceback.print_exc()

    async def monitor_positions(self):
        """Monitor and manage open positions"""
        if not self.positions:
            return

        logger.info(f"\n📊 Monitoring {len(self.positions)} open positions...")

        for position in self.positions[:]:  # Copy list to allow removal
            try:
                symbol = position.symbol

                # Fetch current price
                df = self.fetcher.fetch_klines_sync(
                    symbol=symbol,
                    interval='1m',
                    limit=1
                )

                if df.empty:
                    continue

                current_price = df.iloc[-1]['close']

                # Check stop loss / take profit
                if position.side == 'LONG':
                    if current_price <= position.stop_loss:
                        await self.close_position(position, current_price, 'STOP_LOSS')
                    elif current_price >= position.take_profits[0]:
                        await self.close_position(position, current_price, 'TAKE_PROFIT')
                else:  # SHORT
                    if current_price >= position.stop_loss:
                        await self.close_position(position, current_price, 'STOP_LOSS')
                    elif current_price <= position.take_profits[0]:
                        await self.close_position(position, current_price, 'TAKE_PROFIT')

            except Exception as e:
                logger.error(f"❌ Error monitoring position {position.symbol}: {e}")

    async def close_position(self, position: Position, exit_price: float, reason: str):
        """
        Close a position

        Args:
            position: Position to close
            exit_price: Exit price
            reason: Exit reason (STOP_LOSS, TAKE_PROFIT, etc)
        """
        try:
            # Calculate P&L
            if position.side == 'LONG':
                pnl = (exit_price - position.entry_price) * position.size
            else:
                pnl = (position.entry_price - exit_price) * position.size

            pnl_percent = (pnl / (position.entry_price * position.size)) * 100

            logger.info(f"\n{'='*70}")
            logger.info(f"🔴 CLOSING {position.side} POSITION ON {position.symbol}")
            logger.info(f"{'='*70}")
            logger.info(f"Entry: ${position.entry_price:,.2f}")
            logger.info(f"Exit: ${exit_price:,.2f}")
            logger.info(f"P&L: ${pnl:+,.2f} ({pnl_percent:+.2f}%)")
            logger.info(f"Reason: {reason}")

            # Create trade record
            trade = Trade(
                symbol=position.symbol,
                side=position.side,
                entry_price=position.entry_price,
                exit_price=exit_price,
                size=position.size,
                pnl=pnl,
                pnl_percent=pnl_percent,
                entry_time=position.entry_time,
                exit_time=datetime.now(),
                exit_reason=reason,
                status='CLOSED'
            )

            # Save trade
            self.state_manager.add_trade(trade)

            # Update capital and daily PnL
            self.capital += pnl
            self.daily_pnl += pnl

            # Remove position
            self.state_manager.close_position(position.symbol)
            self.positions.remove(position)

            logger.info(f"✅ Position closed")
            logger.info(f"   New Capital: ${self.capital:,.2f}")
            logger.info(f"   Daily P&L: ${self.daily_pnl:+,.2f}")

        except Exception as e:
            logger.error(f"❌ Error closing position: {e}")

    async def run(self):
        """Main bot loop"""
        self.running = True
        logger.info("\n🚀 Bot started! Press Ctrl+C to stop.\n")

        await self.initialize()

        scan_interval = 60  # Scan every 60 seconds
        monitor_interval = 10  # Monitor positions every 10 seconds
        last_scan = 0
        last_monitor = 0

        try:
            while self.running:
                current_time = asyncio.get_event_loop().time()

                # Scan for new signals
                if current_time - last_scan >= scan_interval:
                    last_scan = current_time

                    # Check if we can take new trades
                    if await self.check_risk_limits():
                        # Scan all allowed pairs
                        for symbol in ALLOWED_PAIRS:
                            signal = await self.scan_market(symbol)

                            if signal and signal.get('has_signal'):
                                await self.execute_trade(signal)
                                break  # Only take one trade per scan

                # Monitor open positions
                if current_time - last_monitor >= monitor_interval:
                    last_monitor = current_time
                    await self.monitor_positions()

                # Sleep briefly
                await asyncio.sleep(1)

        except KeyboardInterrupt:
            logger.info("\n⚠️ Shutdown signal received...")
        except Exception as e:
            logger.error(f"❌ Fatal error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await self.shutdown()

    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("\n🛑 Shutting down bot...")
        self.running = False

        # Close all positions
        if self.positions:
            logger.info(f"⚠️ Closing {len(self.positions)} open positions...")
            for position in self.positions[:]:
                try:
                    # Fetch current price
                    df = self.fetcher.fetch_klines_sync(
                        symbol=position.symbol,
                        interval='1m',
                        limit=1
                    )
                    if not df.empty:
                        current_price = df.iloc[-1]['close']
                        await self.close_position(position, current_price, 'SHUTDOWN')
                except Exception as e:
                    logger.error(f"Error closing position on shutdown: {e}")

        # Stop bot state
        self.state_manager.stop_bot()

        logger.info("✅ Bot stopped successfully")
        logger.info(f"Final Capital: ${self.capital:,.2f}")
        logger.info(f"Total Trades: {self.daily_trades}")
        logger.info(f"Daily P&L: ${self.daily_pnl:+,.2f}")


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info("\n⚠️ Received shutdown signal...")
    sys.exit(0)


async def main(mode: str = "testnet", capital: float = 10000):
    """
    Main entry point

    Args:
        mode: Trading mode ("testnet" or "live")
        capital: Initial capital
    """
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Create and run bot
    use_testnet = (mode.lower() == "testnet")
    bot = TradingBot(testnet=use_testnet)
    bot.capital = capital  # Set initial capital
    await bot.run()


if __name__ == "__main__":
    import argparse

    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Binance Algo Trading Bot")
    parser.add_argument("--mode", type=str, default="testnet",
                       choices=["testnet", "live"],
                       help="Trading mode: testnet or live")
    parser.add_argument("--capital", type=float, default=10000,
                       help="Initial capital (default: 10000)")

    args = parser.parse_args()

    # Run bot with arguments
    asyncio.run(main(mode=args.mode, capital=args.capital))
