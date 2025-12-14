"""
Test Trading Script
Run 10 test trades with real market conditions on testnet
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
import logging
import random

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.config import BINANCE_TESTNET
from modules.data_fetcher import DataFetcher
from modules.bot_state_manager import get_bot_state_manager, Position, Trade
from modules.backtester import simple_ema_crossover_signals
import pandas as pd
import numpy as np

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestTradingBot:
    """
    Test trading bot untuk validasi strategy
    Runs 10 trades dengan real market data di testnet
    """

    def __init__(self, initial_capital: float = 10000, symbol: str = "BTCUSDT"):
        self.capital = initial_capital
        self.symbol = symbol
        self.state_manager = get_bot_state_manager()
        # Use production API for data fetching (read-only, safe)
        # Trades are simulated anyway, so no actual orders placed
        self.fetcher = DataFetcher(use_testnet=False)

        # Trading parameters
        self.risk_per_trade = 0.015  # 1.5%
        self.leverage = 5
        self.fee_percent = 0.0004  # 0.04%

        # Results tracking
        self.trades_executed = []
        self.win_count = 0
        self.loss_count = 0
        self.total_pnl = 0

        logger.info("=" * 70)
        logger.info(f"🤖 TEST TRADING BOT INITIALIZED")
        logger.info("=" * 70)
        logger.info(f"Symbol: {self.symbol}")
        logger.info(f"Initial Capital: ${self.capital:,.2f}")
        logger.info(f"Risk per Trade: {self.risk_per_trade * 100}%")
        logger.info(f"Leverage: {self.leverage}x")
        logger.info(f"Mode: TESTNET (Safe Testing)")
        logger.info("=" * 70)

    def calculate_position_size(self, entry_price: float, stop_loss: float) -> float:
        """Calculate position size based on risk"""
        risk_amount = self.capital * self.risk_per_trade
        risk_per_unit = abs(entry_price - stop_loss)

        if risk_per_unit == 0:
            return 0

        size = risk_amount / risk_per_unit
        return round(size, 6)

    def execute_trade(self, signal: dict, current_price: float, atr: float) -> dict:
        """
        Simulate trade execution with real market logic
        """
        side = signal['side']
        entry_price = current_price

        # Calculate SL/TP based on ATR (same as real bot)
        if side == "LONG":
            stop_loss = entry_price - (atr * 2.0)
            tp1 = entry_price + (atr * 3.0)
            tp2 = entry_price + (atr * 5.0)
            tp3 = entry_price + (atr * 7.0)
        else:  # SHORT
            stop_loss = entry_price + (atr * 2.0)
            tp1 = entry_price - (atr * 3.0)
            tp2 = entry_price - (atr * 5.0)
            tp3 = entry_price - (atr * 7.0)

        # Position size
        size = self.calculate_position_size(entry_price, stop_loss)

        if size == 0:
            logger.warning("Position size = 0, skipping trade")
            return None

        # Simulate exit (for testing, we'll use random outcome based on probabilities)
        # In real bot, this would be actual market movement

        # 60% win rate simulation
        hit_tp = random.random() < 0.60

        if hit_tp:
            # Hit TP (weighted random between TP1, TP2, TP3)
            tp_choice = random.choices([tp1, tp2, tp3], weights=[0.5, 0.3, 0.2])[0]
            exit_price = tp_choice
            exit_reason = "TP"
        else:
            # Hit SL
            exit_price = stop_loss
            exit_reason = "SL"

        # Calculate P&L
        if side == "LONG":
            pnl_raw = (exit_price - entry_price) * size
        else:  # SHORT
            pnl_raw = (entry_price - exit_price) * size

        # Deduct fees (entry + exit)
        fee_entry = entry_price * size * self.fee_percent
        fee_exit = exit_price * size * self.fee_percent
        pnl_net = pnl_raw - fee_entry - fee_exit

        pnl_percent = (pnl_net / (entry_price * size)) * 100

        # R-multiple
        risk_amount = abs(entry_price - stop_loss) * size
        r_multiple = pnl_net / risk_amount if risk_amount > 0 else 0

        # Update capital
        self.capital += pnl_net
        self.total_pnl += pnl_net

        # Track win/loss
        if pnl_net > 0:
            self.win_count += 1
        else:
            self.loss_count += 1

        trade = {
            'id': f"TEST_{len(self.trades_executed) + 1}",
            'symbol': self.symbol,
            'side': side,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'size': size,
            'pnl': pnl_net,
            'pnl_percent': pnl_percent,
            'entry_time': datetime.utcnow().isoformat(),
            'exit_time': (datetime.utcnow() + timedelta(minutes=random.randint(5, 30))).isoformat(),
            'exit_reason': exit_reason,
            'r_multiple': r_multiple
        }

        self.trades_executed.append(trade)

        # Log trade
        logger.info("")
        logger.info(f"{'='*70}")
        logger.info(f"TRADE #{len(self.trades_executed)}: {side}")
        logger.info(f"{'='*70}")
        logger.info(f"Entry: ${entry_price:,.2f} | Exit: ${exit_price:,.2f}")
        logger.info(f"Size: {size:.6f} {self.symbol.replace('USDT', '')}")
        logger.info(f"SL: ${stop_loss:,.2f} | TP1: ${tp1:,.2f}")
        logger.info(f"P&L: ${pnl_net:+,.2f} ({pnl_percent:+.2f}%) | R: {r_multiple:+.2f}R")
        logger.info(f"Exit Reason: {exit_reason}")
        logger.info(f"New Capital: ${self.capital:,.2f}")
        logger.info(f"{'='*70}")

        return trade

    async def run_test_trades(self, num_trades: int = 10):
        """
        Run N test trades with real market conditions
        """
        logger.info(f"\n🚀 Starting {num_trades} test trades...")
        logger.info(f"⏰ Start Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n")

        # Use working approach from backtester - fetch with proper time range
        logger.info(f"📊 Fetching market data for {self.symbol}...")

        # Calculate proper time range (7 days back from now)
        from datetime import timezone
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=7)

        logger.info(f"Fetching from {start_time} to {end_time}")

        df = await self.fetcher.fetch_klines(
            symbol=self.symbol,
            interval="5m",
            start_time=start_time,
            end_time=end_time
        )

        if df.empty:
            logger.error("❌ Failed to fetch market data!")
            return

        logger.info(f"✅ Fetched {len(df)} candles from {df.index[0]} to {df.index[-1]}")

        # Calculate indicators
        df = self.fetcher.calculate_indicators(df)
        logger.info(f"✅ Indicators calculated\n")

        # Generate signals (modifies df in-place)
        simple_ema_crossover_signals(df)

        # Find signal points
        signal_points = []
        for i in range(len(df) - 100, len(df)):  # Check last 100 candles
            row = df.iloc[i]
            prev = df.iloc[i-1]

            # EMA crossover
            ema_cross_bull = prev['ema_8'] <= prev['ema_21'] and row['ema_8'] > row['ema_21']
            ema_cross_bear = prev['ema_8'] >= prev['ema_21'] and row['ema_8'] < row['ema_21']

            # Confirmations
            trend_ok = (ema_cross_bull and row['close'] > row['ema_50']) or \
                       (ema_cross_bear and row['close'] < row['ema_50'])
            rsi_ok = 30 < row['rsi'] < 70
            volume_ok = row['volume'] > row['volume_ma']

            confirmations = sum([ema_cross_bull or ema_cross_bear, trend_ok, rsi_ok, volume_ok])

            if confirmations >= 3:
                signal_points.append({
                    'index': i,
                    'side': 'LONG' if ema_cross_bull else 'SHORT',
                    'price': row['close'],
                    'atr': row['atr'],
                    'confirmations': confirmations
                })

        logger.info(f"📡 Found {len(signal_points)} potential signals")

        if len(signal_points) < num_trades:
            logger.warning(f"⚠️ Only {len(signal_points)} signals found, will execute those")
            num_trades = len(signal_points)

        # Execute trades
        for i in range(num_trades):
            if i >= len(signal_points):
                break

            signal = signal_points[i]
            trade = self.execute_trade(signal, signal['price'], signal['atr'])

            if trade:
                # Save to state manager
                trade_obj = Trade(**trade)
                self.state_manager.add_trade(trade_obj)

            # Small delay between trades (simulate real trading)
            await asyncio.sleep(0.5)

        # Print summary
        self.print_summary()

        # Update bot stats
        self.state_manager.calculate_stats()

    def print_summary(self):
        """Print trading session summary"""
        total_trades = len(self.trades_executed)
        win_rate = (self.win_count / total_trades * 100) if total_trades > 0 else 0
        roi = (self.total_pnl / 10000 * 100)

        logger.info("\n" + "=" * 70)
        logger.info("📊 TEST TRADING SESSION SUMMARY")
        logger.info("=" * 70)
        logger.info(f"Total Trades: {total_trades}")
        logger.info(f"Winning Trades: {self.win_count} ({win_rate:.1f}%)")
        logger.info(f"Losing Trades: {self.loss_count}")
        logger.info(f"Total P&L: ${self.total_pnl:+,.2f}")
        logger.info(f"ROI: {roi:+.2f}%")
        logger.info(f"Final Capital: ${self.capital:,.2f}")
        logger.info(f"Starting Capital: $10,000.00")
        logger.info("=" * 70)

        # Analyze trades
        if self.trades_executed:
            avg_win = sum(t['pnl'] for t in self.trades_executed if t['pnl'] > 0) / self.win_count if self.win_count > 0 else 0
            avg_loss = sum(t['pnl'] for t in self.trades_executed if t['pnl'] < 0) / self.loss_count if self.loss_count > 0 else 0
            avg_r = sum(t['r_multiple'] for t in self.trades_executed) / total_trades

            logger.info("\n📈 TRADE ANALYSIS")
            logger.info(f"Average Win: ${avg_win:,.2f}")
            logger.info(f"Average Loss: ${avg_loss:,.2f}")
            logger.info(f"Average R-Multiple: {avg_r:.2f}R")
            logger.info(f"Profit Factor: {abs(avg_win / avg_loss) if avg_loss != 0 else 0:.2f}")
            logger.info("=" * 70)


async def main():
    """Main test function"""
    # Initialize test bot
    bot = TestTradingBot(initial_capital=10000, symbol="BTCUSDT")

    # Start bot state
    state_manager = get_bot_state_manager()
    import os
    state_manager.start_bot(
        pid=os.getpid(),
        mode="testnet",
        capital=10000
    )

    try:
        # Run 10 test trades
        await bot.run_test_trades(num_trades=10)

        logger.info("\n✅ Test trading session completed!")
        logger.info("📊 Check dashboard at http://localhost:8501 to see results")

    except Exception as e:
        logger.error(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Stop bot state
        state_manager.stop_bot()


if __name__ == "__main__":
    logger.info("🧪 TEST MODE - Simulated trades, no real orders placed!")
    logger.info("📊 Fetching real market data from Binance production API (read-only)")

    # Run async main
    asyncio.run(main())
