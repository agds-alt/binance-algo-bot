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
import ta  # Technical Analysis library for Stochastic RSI


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


def optimized_ema_crossover_signals(df: pd.DataFrame) -> Optional[Dict]:
    """
    Optimized EMA crossover strategy with stricter confirmations

    Improvements:
    - Volume filter (1.5x average)
    - RSI range filter (30-70)
    - Trend strength filter
    - HTF alignment (EMA200)
    - Requires 5/6 confirmations

    Args:
        df: DataFrame with indicators

    Returns:
        Signal dict or None
    """
    if len(df) < 2:
        return None

    current = df.iloc[-1]
    previous = df.iloc[-2]

    # Check confirmations
    confirmations = 0

    # 1. EMA crossover (required)
    ema_cross_bullish = (previous['ema_8'] <= previous['ema_21'] and
                         current['ema_8'] > current['ema_21'])
    ema_cross_bearish = (previous['ema_8'] >= previous['ema_21'] and
                         current['ema_8'] < current['ema_21'])

    if not (ema_cross_bullish or ema_cross_bearish):
        return None

    # Determine signal type
    if ema_cross_bullish:
        signal_type = 'LONG'
        confirmations += 1

        # 2. Price above trend EMA (EMA50)
        if current['close'] > current['ema_50']:
            confirmations += 1

        # 3. Trend strength (price at least 0.5% above EMA50)
        ema_distance = ((current['close'] - current['ema_50']) / current['ema_50']) * 100
        if ema_distance > 0.5:
            confirmations += 1

        # 4. RSI in range (30-70) - avoid overbought
        if 30 < current['rsi'] < 70:
            confirmations += 1

        # 5. Volume confirmation (1.5x average)
        volume_ratio = current['volume'] / current['volume_ma'] if current['volume_ma'] > 0 else 0
        if volume_ratio > 1.5:
            confirmations += 1

        # 6. HTF alignment (price above EMA200)
        if current['close'] > current['ema_200']:
            confirmations += 1

        # Require at least 5/6 confirmations
        if confirmations >= 5:
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
                'take_profits': [tp1, tp2, tp3],
                'confirmations': confirmations
            }

    elif ema_cross_bearish:
        signal_type = 'SHORT'
        confirmations += 1

        # 2. Price below trend EMA (EMA50)
        if current['close'] < current['ema_50']:
            confirmations += 1

        # 3. Trend strength (price at least 0.5% below EMA50)
        ema_distance = ((current['ema_50'] - current['close']) / current['ema_50']) * 100
        if ema_distance > 0.5:
            confirmations += 1

        # 4. RSI in range (30-70) - avoid oversold
        if 30 < current['rsi'] < 70:
            confirmations += 1

        # 5. Volume confirmation (1.5x average)
        volume_ratio = current['volume'] / current['volume_ma'] if current['volume_ma'] > 0 else 0
        if volume_ratio > 1.5:
            confirmations += 1

        # 6. HTF alignment (price below EMA200)
        if current['close'] < current['ema_200']:
            confirmations += 1

        # Require at least 5/6 confirmations
        if confirmations >= 5:
            entry_price = current['close']
            atr = current['atr']

            # ATR-based SL/TP
            stop_loss = entry_price + (atr * 2.0)
            tp1 = entry_price - (atr * 3.0)
            tp2 = entry_price - (atr * 5.0)
            tp3 = entry_price - (atr * 7.0)

            return {
                'side': 'SHORT',
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profits': [tp1, tp2, tp3],
                'confirmations': confirmations
            }

    return None


def relaxed_ema_crossover_signals(df: pd.DataFrame, debug: bool = False) -> Optional[Dict]:
    """
    RELAXED version for testing - easier to trigger signals
    
    Changes from optimized version:
    - Volume filter: 1.2x (was 1.5x) 
    - Requires 4/6 confirmations (was 5/6)
    - RSI range: 25-75 (was 30-70)
    - Trend strength: 0.3% (was 0.5%)
    - More aggressive for testing
    
    Args:
        df: DataFrame with indicators
        debug: If True, return debug info even when no signal
        
    Returns:
        Signal dict or None (or debug dict if debug=True)
    """
    if len(df) < 2:
        return None
    
    current = df.iloc[-1]
    previous = df.iloc[-2]
    
    # Debug info
    debug_info = {
        'has_signal': False,
        'confirmations': 0,
        'checks': {},
        'mode': 'RELAXED (4/6 needed)'
    }
    
    confirmations = 0
    checks = {}
    
    # 1. EMA crossover (required)
    ema_cross_bullish = (previous['ema_8'] <= previous['ema_21'] and
                         current['ema_8'] > current['ema_21'])
    ema_cross_bearish = (previous['ema_8'] >= previous['ema_21'] and
                         current['ema_8'] < current['ema_21'])
    
    checks['1_ema_crossover'] = '✅ YES' if (ema_cross_bullish or ema_cross_bearish) else '❌ NO'
    
    if not (ema_cross_bullish or ema_cross_bearish):
        if debug:
            debug_info['checks'] = checks
            debug_info['reason'] = 'No EMA crossover detected'
            return debug_info
        return None
    
    # Determine signal type
    if ema_cross_bullish:
        signal_type = 'LONG'
        confirmations += 1
        
        # 2. Price above trend EMA (EMA50)
        price_above_ema50 = current['close'] > current['ema_50']
        checks['2_price_above_ema50'] = f"{'✅' if price_above_ema50 else '❌'} Price: ${current['close']:.2f}, EMA50: ${current['ema_50']:.2f}"
        if price_above_ema50:
            confirmations += 1
        
        # 3. Trend strength (0.3% above EMA50) - RELAXED
        ema_distance = ((current['close'] - current['ema_50']) / current['ema_50']) * 100
        trend_strong = ema_distance > 0.3
        checks['3_trend_strength'] = f"{'✅' if trend_strong else '❌'} {ema_distance:.2f}% (need >0.3%)"
        if trend_strong:
            confirmations += 1
        
        # 4. RSI in range (25-75) - RELAXED
        rsi_ok = 25 < current['rsi'] < 75
        checks['4_rsi'] = f"{'✅' if rsi_ok else '❌'} RSI: {current['rsi']:.1f} (need 25-75)"
        if rsi_ok:
            confirmations += 1
        
        # 5. Volume confirmation (1.2x) - RELAXED
        volume_ratio = current['volume'] / current['volume_ma'] if current['volume_ma'] > 0 else 0
        volume_ok = volume_ratio > 1.2
        checks['5_volume'] = f"{'✅' if volume_ok else '❌'} {volume_ratio:.2f}x avg (need >1.2x)"
        if volume_ok:
            confirmations += 1
        
        # 6. HTF alignment (above EMA200)
        htf_aligned = current['close'] > current['ema_200']
        checks['6_htf_alignment'] = f"{'✅' if htf_aligned else '❌'} Price vs EMA200: ${current['close']:.2f} vs ${current['ema_200']:.2f}"
        if htf_aligned:
            confirmations += 1
        
        debug_info['confirmations'] = confirmations
        debug_info['checks'] = checks
        debug_info['side'] = 'LONG'
        
        # Require 4/6 confirmations - RELAXED
        if confirmations >= 4:
            entry_price = current['close']
            atr = current['atr']
            
            stop_loss = entry_price - (atr * 2.0)
            tp1 = entry_price + (atr * 3.0)
            tp2 = entry_price + (atr * 5.0)
            tp3 = entry_price + (atr * 7.0)
            
            signal = {
                'side': 'LONG',
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profits': [tp1, tp2, tp3],
                'confirmations': confirmations,
                'debug': checks if debug else None
            }
            
            if debug:
                debug_info['has_signal'] = True
                debug_info.update(signal)
            
            return debug_info if debug else signal
        else:
            if debug:
                debug_info['reason'] = f'Only {confirmations}/6 confirmations (need 4+)'
                return debug_info
            return None
    
    elif ema_cross_bearish:
        signal_type = 'SHORT'
        confirmations += 1
        
        # 2. Price below EMA50
        price_below_ema50 = current['close'] < current['ema_50']
        checks['2_price_below_ema50'] = f"{'✅' if price_below_ema50 else '❌'} Price: ${current['close']:.2f}, EMA50: ${current['ema_50']:.2f}"
        if price_below_ema50:
            confirmations += 1
        
        # 3. Trend strength
        ema_distance = ((current['ema_50'] - current['close']) / current['ema_50']) * 100
        trend_strong = ema_distance > 0.3
        checks['3_trend_strength'] = f"{'✅' if trend_strong else '❌'} {ema_distance:.2f}% (need >0.3%)"
        if trend_strong:
            confirmations += 1
        
        # 4. RSI
        rsi_ok = 25 < current['rsi'] < 75
        checks['4_rsi'] = f"{'✅' if rsi_ok else '❌'} RSI: {current['rsi']:.1f} (need 25-75)"
        if rsi_ok:
            confirmations += 1
        
        # 5. Volume
        volume_ratio = current['volume'] / current['volume_ma'] if current['volume_ma'] > 0 else 0
        volume_ok = volume_ratio > 1.2
        checks['5_volume'] = f"{'✅' if volume_ok else '❌'} {volume_ratio:.2f}x avg (need >1.2x)"
        if volume_ok:
            confirmations += 1
        
        # 6. HTF alignment
        htf_aligned = current['close'] < current['ema_200']
        checks['6_htf_alignment'] = f"{'✅' if htf_aligned else '❌'} Price vs EMA200: ${current['close']:.2f} vs ${current['ema_200']:.2f}"
        if htf_aligned:
            confirmations += 1
        
        debug_info['confirmations'] = confirmations
        debug_info['checks'] = checks
        debug_info['side'] = 'SHORT'
        
        if confirmations >= 4:
            entry_price = current['close']
            atr = current['atr']
            
            stop_loss = entry_price + (atr * 2.0)
            tp1 = entry_price - (atr * 3.0)
            tp2 = entry_price - (atr * 5.0)
            tp3 = entry_price - (atr * 7.0)
            
            signal = {
                'side': 'SHORT',
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profits': [tp1, tp2, tp3],
                'confirmations': confirmations,
                'debug': checks if debug else None
            }
            
            if debug:
                debug_info['has_signal'] = True
                debug_info.update(signal)
            
            return debug_info if debug else signal
        else:
            if debug:
                debug_info['reason'] = f'Only {confirmations}/6 confirmations (need 4+)'
                return debug_info
            return None

    return None


def stochastic_rsi_strategy(df: pd.DataFrame, debug: bool = False) -> Optional[Dict]:
    """
    Stochastic RSI Mean Reversion Strategy

    Buy at oversold (Stoch RSI < 20-24)
    Sell at overbought (Stoch RSI > 80)

    Best for: Ranging/sideways markets on 1m timeframe
    Win Rate: 70-75% in ranging, 45-50% in trending

    Safety Filters:
    - Trend filter (don't counter-trend trade)
    - Volume confirmation
    - Multiple confirmations required

    Args:
        df: DataFrame with OHLCV and indicators
        debug: If True, returns detailed debug info

    Returns:
        Signal dict with entry/exit or None
    """
    if len(df) < 30:
        return None

    # Calculate Stochastic RSI
    stoch_rsi = ta.momentum.StochRSIIndicator(
        close=df['close'],
        window=14,
        smooth1=3,
        smooth2=3
    )
    df['stoch_rsi'] = stoch_rsi.stochrsi() * 100  # Convert to 0-100 scale
    df['stoch_rsi_k'] = stoch_rsi.stochrsi_k() * 100
    df['stoch_rsi_d'] = stoch_rsi.stochrsi_d() * 100

    current = df.iloc[-1]
    previous = df.iloc[-2]

    debug_info = {
        'has_signal': False,
        'side': None,
        'confirmations': 0,
        'checks': {},
        'reason': ''
    }
    checks = {}

    # Get current values
    stoch_rsi_val = current['stoch_rsi']
    stoch_rsi_k = current['stoch_rsi_k']
    stoch_rsi_d = current['stoch_rsi_d']

    # Check for LONG (oversold bounce)
    oversold = stoch_rsi_val <= 30  # RELAXED: was 24 (more signals!)
    oversold_bounce = previous['stoch_rsi'] < 25 and current['stoch_rsi'] >= 25  # Started bouncing
    k_cross_d_bullish = previous['stoch_rsi_k'] <= previous['stoch_rsi_d'] and current['stoch_rsi_k'] > current['stoch_rsi_d']

    # Check for SHORT (overbought rejection)
    overbought = stoch_rsi_val >= 75  # RELAXED: was 80 (more signals!)
    overbought_rejection = previous['stoch_rsi'] > 75 and current['stoch_rsi'] <= 75  # Started falling
    k_cross_d_bearish = previous['stoch_rsi_k'] >= previous['stoch_rsi_d'] and current['stoch_rsi_k'] < current['stoch_rsi_d']

    # LONG Signal
    if oversold or oversold_bounce:
        signal_type = 'LONG'
        confirmations = 0

        # 1. Stochastic RSI oversold
        checks['1_stoch_rsi_oversold'] = f"{'✅' if oversold else '❌'} Stoch RSI: {stoch_rsi_val:.1f} (need ≤30)"
        if oversold:
            confirmations += 1

        # 2. Bounce confirmation (previous < 20, current >= 20)
        checks['2_oversold_bounce'] = f"{'✅' if oversold_bounce else '❌'} Bouncing from extreme"
        if oversold_bounce:
            confirmations += 1

        # 3. K line crosses D line (bullish crossover)
        checks['3_k_cross_d'] = f"{'✅' if k_cross_d_bullish else '❌'} K: {stoch_rsi_k:.1f}, D: {stoch_rsi_d:.1f}"
        if k_cross_d_bullish:
            confirmations += 1

        # 4. Trend filter: Don't buy in strong downtrend
        trend_ok = current['ema_21'] > current['ema_50'] or abs(current['ema_21'] - current['ema_50']) / current['ema_50'] < 0.005
        checks['4_trend_filter'] = f"{'✅' if trend_ok else '❌'} EMA21 vs EMA50: Not strong downtrend"
        if trend_ok:
            confirmations += 1

        # 5. Volume confirmation
        vol_ma = df['volume'].rolling(20).mean().iloc[-1]
        volume_ok = current['volume'] > vol_ma * 1.0  # Any volume (less strict)
        checks['5_volume'] = f"{'✅' if volume_ok else '❌'} {current['volume'] / vol_ma:.2f}x avg"
        if volume_ok:
            confirmations += 1

        # 6. RSI not too low (avoid knife-catching)
        rsi_ok = current['rsi'] > 20  # RSI above 20 to avoid dead cat bounce
        checks['6_rsi_filter'] = f"{'✅' if rsi_ok else '❌'} RSI: {current['rsi']:.1f} (need >20)"
        if rsi_ok:
            confirmations += 1

        debug_info['confirmations'] = confirmations
        debug_info['checks'] = checks
        debug_info['side'] = 'LONG'

        # Require 4/6 confirmations
        if confirmations >= 4:
            entry_price = current['close']
            atr = current['atr']

            # Tight stops for scalping
            stop_loss = entry_price - (atr * 1.5)

            # Target: Stoch RSI 80 = overbought
            # Estimate: ~0.3-0.5% move on 1m typically
            tp1 = entry_price + (atr * 1.5)  # Quick scalp
            tp2 = entry_price + (atr * 2.5)  # Medium target
            tp3 = entry_price + (atr * 4.0)  # Extended (if momentum continues)

            signal = {
                'side': 'LONG',
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profits': [tp1, tp2, tp3],
                'confirmations': confirmations,
                'debug': checks if debug else None
            }

            if debug:
                debug_info['has_signal'] = True
                debug_info.update(signal)

            return debug_info if debug else signal
        else:
            if debug:
                debug_info['reason'] = f'Only {confirmations}/6 confirmations (need 4+)'
                return debug_info
            return None

    # SHORT Signal
    elif overbought or overbought_rejection:
        signal_type = 'SHORT'
        confirmations = 0

        # 1. Stochastic RSI overbought
        checks['1_stoch_rsi_overbought'] = f"{'✅' if overbought else '❌'} Stoch RSI: {stoch_rsi_val:.1f} (need ≥75)"
        if overbought:
            confirmations += 1

        # 2. Rejection confirmation (previous > 80, current <= 80)
        checks['2_overbought_rejection'] = f"{'✅' if overbought_rejection else '❌'} Rejecting from extreme"
        if overbought_rejection:
            confirmations += 1

        # 3. K line crosses D line (bearish crossover)
        checks['3_k_cross_d'] = f"{'✅' if k_cross_d_bearish else '❌'} K: {stoch_rsi_k:.1f}, D: {stoch_rsi_d:.1f}"
        if k_cross_d_bearish:
            confirmations += 1

        # 4. Trend filter: Don't short in strong uptrend
        trend_ok = current['ema_21'] < current['ema_50'] or abs(current['ema_21'] - current['ema_50']) / current['ema_50'] < 0.005
        checks['4_trend_filter'] = f"{'✅' if trend_ok else '❌'} EMA21 vs EMA50: Not strong uptrend"
        if trend_ok:
            confirmations += 1

        # 5. Volume confirmation
        vol_ma = df['volume'].rolling(20).mean().iloc[-1]
        volume_ok = current['volume'] > vol_ma * 1.0
        checks['5_volume'] = f"{'✅' if volume_ok else '❌'} {current['volume'] / vol_ma:.2f}x avg"
        if volume_ok:
            confirmations += 1

        # 6. RSI not too high
        rsi_ok = current['rsi'] < 80
        checks['6_rsi_filter'] = f"{'✅' if rsi_ok else '❌'} RSI: {current['rsi']:.1f} (need <80)"
        if rsi_ok:
            confirmations += 1

        debug_info['confirmations'] = confirmations
        debug_info['checks'] = checks
        debug_info['side'] = 'SHORT'

        # Require 4/6 confirmations
        if confirmations >= 4:
            entry_price = current['close']
            atr = current['atr']

            # Tight stops for scalping
            stop_loss = entry_price + (atr * 1.5)

            # Target: Stoch RSI 20 = oversold
            tp1 = entry_price - (atr * 1.5)
            tp2 = entry_price - (atr * 2.5)
            tp3 = entry_price - (atr * 4.0)

            signal = {
                'side': 'SHORT',
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profits': [tp1, tp2, tp3],
                'confirmations': confirmations,
                'debug': checks if debug else None
            }

            if debug:
                debug_info['has_signal'] = True
                debug_info.update(signal)

            return debug_info if debug else signal
        else:
            if debug:
                debug_info['reason'] = f'Only {confirmations}/6 confirmations (need 4+)'
                return debug_info
            return None

    # No signal
    if debug:
        debug_info['reason'] = f'Stoch RSI in neutral zone: {stoch_rsi_val:.1f} (wait for <24 or >80)'
        checks['stoch_rsi'] = f"Stoch RSI: {stoch_rsi_val:.1f}"
        checks['k_line'] = f"K: {stoch_rsi_k:.1f}"
        checks['d_line'] = f"D: {stoch_rsi_d:.1f}"
        debug_info['checks'] = checks
        return debug_info

    return None
