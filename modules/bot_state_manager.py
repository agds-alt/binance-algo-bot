"""
Bot State Manager
Manages shared state between trading bot and dashboard
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import fcntl
import os


@dataclass
class BotState:
    """Bot running state"""
    is_running: bool = False
    pid: Optional[int] = None
    started_at: Optional[str] = None
    stopped_at: Optional[str] = None
    mode: str = "testnet"  # testnet or live
    capital: float = 0.0
    uptime_seconds: int = 0


@dataclass
class Position:
    """Open position"""
    symbol: str
    side: str  # LONG or SHORT
    entry_price: float
    current_price: float
    size: float
    pnl: float
    pnl_percent: float
    stop_loss: float
    take_profits: List[float]
    entry_time: str
    unrealized_pnl: float = 0.0


@dataclass
class Trade:
    """Completed trade"""
    id: str
    symbol: str
    side: str
    entry_price: float
    exit_price: float
    size: float
    pnl: float
    pnl_percent: float
    entry_time: str
    exit_time: str
    exit_reason: str
    r_multiple: float


@dataclass
class BotStats:
    """Bot statistics"""
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0
    total_pnl: float = 0.0
    total_pnl_percent: float = 0.0
    today_pnl: float = 0.0
    today_trades: int = 0
    signals_today: int = 0
    current_balance: float = 0.0
    peak_balance: float = 0.0
    drawdown: float = 0.0
    drawdown_percent: float = 0.0
    # Additional metrics
    avg_win: float = 0.0
    avg_loss: float = 0.0
    best_trade: float = 0.0
    worst_trade: float = 0.0


class BotStateManager:
    """
    Manages bot state files for communication between bot and dashboard

    Files:
    - data/bot_state.json: Bot running status
    - data/positions.json: Current open positions
    - data/trades.json: Recent trades (last 100)
    - data/bot_stats.json: Bot performance statistics
    """

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.state_file = self.data_dir / "bot_state.json"
        self.positions_file = self.data_dir / "positions.json"
        self.trades_file = self.data_dir / "trades.json"
        self.stats_file = self.data_dir / "bot_stats.json"

    def _read_json(self, file_path: Path, default: dict) -> dict:
        """Read JSON file with file locking"""
        if not file_path.exists():
            return default

        try:
            with open(file_path, 'r') as f:
                # Lock file for reading
                fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                data = json.load(f)
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                return data
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return default

    def _write_json(self, file_path: Path, data: dict):
        """Write JSON file with file locking"""
        try:
            with open(file_path, 'w') as f:
                # Lock file for writing
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                json.dump(data, f, indent=2)
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        except Exception as e:
            print(f"Error writing {file_path}: {e}")

    # Bot State Management
    def get_bot_state(self) -> BotState:
        """Get current bot state"""
        data = self._read_json(self.state_file, {})
        return BotState(**data) if data else BotState()

    def set_bot_state(self, state: BotState):
        """Update bot state"""
        self._write_json(self.state_file, asdict(state))

    def start_bot(self, pid: int, mode: str, capital: float):
        """Mark bot as started"""
        state = BotState(
            is_running=True,
            pid=pid,
            started_at=datetime.utcnow().isoformat(),
            stopped_at=None,
            mode=mode,
            capital=capital,
            uptime_seconds=0
        )
        self.set_bot_state(state)

    def stop_bot(self):
        """Mark bot as stopped"""
        state = self.get_bot_state()
        state.is_running = False
        state.stopped_at = datetime.utcnow().isoformat()
        state.pid = None
        self.set_bot_state(state)

    def update_uptime(self):
        """Update bot uptime"""
        state = self.get_bot_state()
        if state.is_running and state.started_at:
            started = datetime.fromisoformat(state.started_at)
            uptime = (datetime.utcnow() - started).seconds
            state.uptime_seconds = uptime
            self.set_bot_state(state)

    # Positions Management
    def get_positions(self) -> List[Position]:
        """Get all open positions"""
        data = self._read_json(self.positions_file, [])
        return [Position(**p) for p in data]

    def set_positions(self, positions: List[Position]):
        """Update positions"""
        data = [asdict(p) for p in positions]
        self._write_json(self.positions_file, data)

    def add_position(self, position: Position):
        """Add a new position"""
        positions = self.get_positions()
        positions.append(position)
        self.set_positions(positions)

    def remove_position(self, symbol: str):
        """Remove position by symbol"""
        positions = self.get_positions()
        positions = [p for p in positions if p.symbol != symbol]
        self.set_positions(positions)

    def update_position_price(self, symbol: str, current_price: float):
        """Update position current price and P&L"""
        positions = self.get_positions()
        for pos in positions:
            if pos.symbol == symbol:
                pos.current_price = current_price

                if pos.side == "LONG":
                    pos.unrealized_pnl = (current_price - pos.entry_price) * pos.size
                else:  # SHORT
                    pos.unrealized_pnl = (pos.entry_price - current_price) * pos.size

                pos.pnl = pos.unrealized_pnl
                pos.pnl_percent = (pos.pnl / (pos.entry_price * pos.size)) * 100

        self.set_positions(positions)

    # Trades Management
    def get_trades(self, limit: int = 100) -> List[Trade]:
        """Get recent trades"""
        data = self._read_json(self.trades_file, [])
        trades = [Trade(**t) for t in data]
        return trades[:limit]

    def add_trade(self, trade: Trade):
        """Add a completed trade"""
        trades = self.get_trades(limit=100)
        trades.insert(0, trade)  # Add to beginning
        trades = trades[:100]  # Keep only last 100

        data = [asdict(t) for t in trades]
        self._write_json(self.trades_file, data)

    # Statistics Management
    def get_stats(self) -> BotStats:
        """Get bot statistics"""
        data = self._read_json(self.stats_file, {})
        return BotStats(**data) if data else BotStats()

    def update_stats(self, stats: BotStats):
        """Update bot statistics"""
        self._write_json(self.stats_file, asdict(stats))

    def calculate_stats(self):
        """Calculate statistics from trades"""
        trades = self.get_trades()
        positions = self.get_positions()

        if not trades and not positions:
            return BotStats()

        # Calculate from trades
        total_trades = len(trades)
        winning_trades = sum(1 for t in trades if t.pnl > 0)
        losing_trades = sum(1 for t in trades if t.pnl < 0)
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

        total_pnl = sum(t.pnl for t in trades)

        # Today's stats
        today = datetime.utcnow().date()
        today_trades = [
            t for t in trades
            if datetime.fromisoformat(t.exit_time).date() == today
        ]
        today_pnl = sum(t.pnl for t in today_trades)

        # Current balance (initial + total P&L)
        state = self.get_bot_state()
        initial_capital = state.capital or 10000
        current_balance = initial_capital + total_pnl

        # Peak and drawdown
        peak_balance = current_balance  # Simplified
        drawdown = 0  # TODO: Calculate properly
        drawdown_percent = 0

        # Calculate avg win/loss and best/worst trades
        winning_pnls = [t.pnl for t in trades if t.pnl > 0]
        losing_pnls = [t.pnl for t in trades if t.pnl < 0]

        avg_win = sum(winning_pnls) / len(winning_pnls) if winning_pnls else 0
        avg_loss = sum(losing_pnls) / len(losing_pnls) if losing_pnls else 0
        best_trade = max([t.pnl for t in trades]) if trades else 0
        worst_trade = min([t.pnl for t in trades]) if trades else 0

        stats = BotStats(
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            total_pnl=total_pnl,
            total_pnl_percent=(total_pnl / initial_capital * 100) if initial_capital > 0 else 0,
            today_pnl=today_pnl,
            today_trades=len(today_trades),
            signals_today=0,  # TODO: Track signals
            current_balance=current_balance,
            peak_balance=peak_balance,
            drawdown=drawdown,
            drawdown_percent=drawdown_percent,
            avg_win=avg_win,
            avg_loss=avg_loss,
            best_trade=best_trade,
            worst_trade=worst_trade
        )

        self.update_stats(stats)
        return stats


# Global singleton
_state_manager = None

def get_bot_state_manager() -> BotStateManager:
    """Get global bot state manager instance"""
    global _state_manager
    if _state_manager is None:
        _state_manager = BotStateManager()
    return _state_manager
