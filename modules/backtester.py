"""
Backtesting Engine
Test trading strategy on historical data
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
import json


@dataclass
class BacktestTrade:
    """Single backtest trade"""
    entry_time: datetime
    exit_time: Optional[datetime]
    symbol: str
    side: str  # 'LONG' or 'SHORT'
    entry_price: float
    exit_price: Optional[float]
    stop_loss: float
    take_profits: List[float]
    position_size: float
    pnl: float = 0.0
    pnl_percent: float = 0.0
    r_multiple: float = 0.0
    exit_reason: str = ''
    fees: float = 0.0
    status: str = 'OPEN'  # OPEN, CLOSED, STOPPED_OUT


@dataclass
class BacktestResult:
    """Backtest results summary"""
    # General info
    symbol: str
    timeframe: str
    start_date: datetime
    end_date: datetime
    duration_days: int

    # Capital
    initial_capital: float
    final_capital: float
    total_return: float
    total_return_percent: float

    # Trades
    total_trades: int
    winning_trades: int
    losing_trades: int
    breakeven_trades: int
    win_rate: float

    # Performance
    gross_profit: float
    gross_loss: float
    net_profit: float
    profit_factor: float
    average_win: float
    average_loss: float
    average_rr: float
    largest_win: float
    largest_loss: float

    # Risk metrics
    max_drawdown: float
    max_drawdown_percent: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float

    # Equity curve
    equity_curve: List[float]
    equity_dates: List[datetime]
    drawdown_curve: List[float]

    # Trade log
    trades: List[Dict]

    def to_dict(self):
        """Convert to dictionary"""
        data = asdict(self)
        # Convert datetime objects
        data['start_date'] = self.start_date.isoformat()
        data['end_date'] = self.end_date.isoformat()
        data['equity_dates'] = [d.isoformat() for d in self.equity_dates]
        return data


class Backtester:
    """
    Backtesting engine for trading strategies

    Tests strategy on historical data and generates performance metrics
    """

    def __init__(
        self,
        initial_capital: float = 10000,
        risk_per_trade: float = 0.015,  # 1.5%
        fee_percent: float = 0.0004,    # 0.04% taker fee
        slippage_percent: float = 0.0005  # 0.05% slippage
    ):
        """
        Initialize backtester

        Args:
            initial_capital: Starting capital
            risk_per_trade: Risk per trade (fraction of capital)
            fee_percent: Trading fee percentage
            slippage_percent: Slippage percentage
        """
        self.initial_capital = initial_capital
        self.risk_per_trade = risk_per_trade
        self.fee_percent = fee_percent
        self.slippage_percent = slippage_percent

        self.capital = initial_capital
        self.equity_curve = [initial_capital]
        self.equity_dates = []
        self.trades: List[BacktestTrade] = []
        self.open_trades: List[BacktestTrade] = []

    def calculate_position_size(
        self,
        entry_price: float,
        stop_loss: float,
        side: str
    ) -> float:
        """
        Calculate position size based on risk

        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            side: 'LONG' or 'SHORT'

        Returns:
            Position size in base currency
        """
        # Calculate risk per unit
        if side == 'LONG':
            risk_per_unit = entry_price - stop_loss
        else:
            risk_per_unit = stop_loss - entry_price

        if risk_per_unit <= 0:
            return 0

        # Risk amount in dollars
        risk_amount = self.capital * self.risk_per_trade

        # Position size
        position_size = risk_amount / risk_per_unit

        return position_size

    def enter_trade(
        self,
        timestamp: datetime,
        symbol: str,
        side: str,
        entry_price: float,
        stop_loss: float,
        take_profits: List[float]
    ) -> Optional[BacktestTrade]:
        """
        Enter a new trade

        Args:
            timestamp: Entry timestamp
            symbol: Trading pair
            side: 'LONG' or 'SHORT'
            entry_price: Entry price
            stop_loss: Stop loss price
            take_profits: List of TP prices

        Returns:
            BacktestTrade or None if position size too small
        """
        # Calculate position size
        position_size = self.calculate_position_size(entry_price, stop_loss, side)

        if position_size <= 0:
            return None

        # Apply slippage
        if side == 'LONG':
            entry_price *= (1 + self.slippage_percent)
        else:
            entry_price *= (1 - self.slippage_percent)

        # Entry fees
        entry_fees = position_size * entry_price * self.fee_percent

        # Create trade
        trade = BacktestTrade(
            entry_time=timestamp,
            exit_time=None,
            symbol=symbol,
            side=side,
            entry_price=entry_price,
            exit_price=None,
            stop_loss=stop_loss,
            take_profits=take_profits,
            position_size=position_size,
            fees=entry_fees,
            status='OPEN'
        )

        self.open_trades.append(trade)

        return trade

    def check_exit(
        self,
        trade: BacktestTrade,
        current_price: float,
        high: float,
        low: float,
        timestamp: datetime
    ) -> bool:
        """
        Check if trade should exit

        Args:
            trade: Open trade
            current_price: Current close price
            high: Current high
            low: Current low
            timestamp: Current timestamp

        Returns:
            True if exited
        """
        if trade.side == 'LONG':
            # Check stop loss
            if low <= trade.stop_loss:
                self._exit_trade(trade, trade.stop_loss, timestamp, 'STOP_LOSS')
                return True

            # Check take profits
            for i, tp in enumerate(trade.take_profits):
                if high >= tp:
                    self._exit_trade(trade, tp, timestamp, f'TP{i+1}')
                    return True

        else:  # SHORT
            # Check stop loss
            if high >= trade.stop_loss:
                self._exit_trade(trade, trade.stop_loss, timestamp, 'STOP_LOSS')
                return True

            # Check take profits
            for i, tp in enumerate(trade.take_profits):
                if low <= tp:
                    self._exit_trade(trade, tp, timestamp, f'TP{i+1}')
                    return True

        return False

    def _exit_trade(
        self,
        trade: BacktestTrade,
        exit_price: float,
        timestamp: datetime,
        reason: str
    ):
        """Exit a trade and calculate P&L"""
        # Apply slippage
        if trade.side == 'LONG':
            exit_price *= (1 - self.slippage_percent)
        else:
            exit_price *= (1 + self.slippage_percent)

        # Exit fees
        exit_fees = trade.position_size * exit_price * self.fee_percent

        # Calculate P&L
        if trade.side == 'LONG':
            pnl = (exit_price - trade.entry_price) * trade.position_size
        else:
            pnl = (trade.entry_price - exit_price) * trade.position_size

        # Subtract fees
        pnl -= (trade.fees + exit_fees)

        # Calculate R multiple
        risk_amount = self.capital * self.risk_per_trade
        r_multiple = pnl / risk_amount if risk_amount > 0 else 0

        # Update trade
        trade.exit_time = timestamp
        trade.exit_price = exit_price
        trade.pnl = pnl
        trade.pnl_percent = (pnl / (trade.position_size * trade.entry_price)) * 100
        trade.r_multiple = r_multiple
        trade.exit_reason = reason
        trade.fees += exit_fees
        trade.status = 'CLOSED'

        # Update capital
        self.capital += pnl

        # Move to closed trades
        self.trades.append(trade)
        self.open_trades.remove(trade)

    def run_backtest(
        self,
        df: pd.DataFrame,
        symbol: str,
        generate_signals_func,
        timeframe: str = '5m'
    ) -> BacktestResult:
        """
        Run backtest on historical data

        Args:
            df: DataFrame with OHLCV + indicators
            symbol: Trading pair
            generate_signals_func: Function that generates trade signals
            timeframe: Timeframe

        Returns:
            BacktestResult
        """
        # Reset state
        self.capital = self.initial_capital
        self.equity_curve = [self.initial_capital]
        self.equity_dates = [df.index[0]]
        self.trades = []
        self.open_trades = []

        # Iterate through data
        for i in range(len(df)):
            row = df.iloc[i]
            timestamp = df.index[i]

            # Check exits for open trades
            for trade in self.open_trades.copy():
                self.check_exit(
                    trade,
                    row['close'],
                    row['high'],
                    row['low'],
                    timestamp
                )

            # Generate new signals
            if i >= 200:  # Need enough data for indicators
                signal = generate_signals_func(df.iloc[:i+1])

                if signal and len(self.open_trades) == 0:  # Max 1 position
                    self.enter_trade(
                        timestamp,
                        symbol,
                        signal['side'],
                        signal['entry_price'],
                        signal['stop_loss'],
                        signal['take_profits']
                    )

            # Update equity curve
            self.equity_curve.append(self.capital)
            self.equity_dates.append(timestamp)

        # Close any remaining open trades
        for trade in self.open_trades.copy():
            self._exit_trade(
                trade,
                df.iloc[-1]['close'],
                df.index[-1],
                'END_OF_DATA'
            )

        # Calculate metrics
        return self._calculate_results(df, symbol, timeframe)

    def _calculate_results(
        self,
        df: pd.DataFrame,
        symbol: str,
        timeframe: str
    ) -> BacktestResult:
        """Calculate backtest results"""
        # Basic stats
        total_trades = len(self.trades)
        winning_trades = sum(1 for t in self.trades if t.pnl > 0)
        losing_trades = sum(1 for t in self.trades if t.pnl < 0)
        breakeven_trades = sum(1 for t in self.trades if t.pnl == 0)

        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

        # P&L stats
        gross_profit = sum(t.pnl for t in self.trades if t.pnl > 0)
        gross_loss = abs(sum(t.pnl for t in self.trades if t.pnl < 0))
        net_profit = self.capital - self.initial_capital

        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else 0

        average_win = (gross_profit / winning_trades) if winning_trades > 0 else 0
        average_loss = (gross_loss / losing_trades) if losing_trades > 0 else 0

        average_rr = np.mean([t.r_multiple for t in self.trades]) if self.trades else 0

        largest_win = max([t.pnl for t in self.trades], default=0)
        largest_loss = min([t.pnl for t in self.trades], default=0)

        # Drawdown
        equity_array = np.array(self.equity_curve)
        running_max = np.maximum.accumulate(equity_array)
        drawdown = (equity_array - running_max) / running_max * 100
        max_drawdown_percent = abs(min(drawdown))
        max_drawdown = abs(min(equity_array - running_max))

        # Sharpe ratio
        returns = np.diff(equity_array) / equity_array[:-1]
        sharpe_ratio = (
            (np.mean(returns) / np.std(returns)) * np.sqrt(252)
            if len(returns) > 0 and np.std(returns) > 0
            else 0
        )

        # Sortino ratio
        negative_returns = returns[returns < 0]
        sortino_ratio = (
            (np.mean(returns) / np.std(negative_returns)) * np.sqrt(252)
            if len(negative_returns) > 0 and np.std(negative_returns) > 0
            else 0
        )

        # Calmar ratio
        calmar_ratio = (
            (net_profit / self.initial_capital * 100) / max_drawdown_percent
            if max_drawdown_percent > 0
            else 0
        )

        # Create result
        result = BacktestResult(
            symbol=symbol,
            timeframe=timeframe,
            start_date=df.index[0],
            end_date=df.index[-1],
            duration_days=(df.index[-1] - df.index[0]).days,
            initial_capital=self.initial_capital,
            final_capital=self.capital,
            total_return=net_profit,
            total_return_percent=(net_profit / self.initial_capital) * 100,
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            breakeven_trades=breakeven_trades,
            win_rate=win_rate,
            gross_profit=gross_profit,
            gross_loss=gross_loss,
            net_profit=net_profit,
            profit_factor=profit_factor,
            average_win=average_win,
            average_loss=average_loss,
            average_rr=average_rr,
            largest_win=largest_win,
            largest_loss=largest_loss,
            max_drawdown=max_drawdown,
            max_drawdown_percent=max_drawdown_percent,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            calmar_ratio=calmar_ratio,
            equity_curve=self.equity_curve,
            equity_dates=self.equity_dates,
            drawdown_curve=drawdown.tolist(),
            trades=[asdict(t) for t in self.trades]
        )

        return result


# Example signal generation function
def simple_ema_crossover_signals(df: pd.DataFrame) -> Optional[Dict]:
    """
    Simple EMA crossover strategy

    Args:
        df: DataFrame with indicators

    Returns:
        Signal dict or None
    """
    if len(df) < 2:
        return None

    current = df.iloc[-1]
    previous = df.iloc[-2]

    # Long signal: EMA8 crosses above EMA21
    if (previous['ema_8'] <= previous['ema_21'] and
        current['ema_8'] > current['ema_21'] and
        current['close'] > current['ema_50']):  # Above trend

        entry_price = current['close']
        atr = current['atr']

        # ATR-based SL/TP
        stop_loss = entry_price - (atr * 2.0)
        tp1 = entry_price + (atr * 3.0)
        tp2 = entry_price + (atr * 5.0)
        tp3 = entry_price + (atr * 7.0)

        return {
            'side': 'LONG',
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'take_profits': [tp1, tp2, tp3]
        }

    return None
