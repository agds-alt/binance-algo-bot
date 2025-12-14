"""
Risk Management Module
Implements hard limits and safety checks that CANNOT be overridden
"""

import logging
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PositionSize:
    """Position sizing calculation result"""
    amount: float  # Position size in base currency
    value_usd: float  # Position value in USD
    leverage: int  # Leverage to use
    risk_usd: float  # Dollar risk on this trade
    risk_percent: float  # Percentage risk


@dataclass
class TradeValidation:
    """Trade validation result"""
    is_valid: bool
    message: str
    failed_checks: list


class RiskManager:
    """
    Core Risk Management System

    CRITICAL: This class enforces hard limits that protect capital.
    NO OVERRIDES ALLOWED.
    """

    def __init__(self, config: Dict):
        self.config = config['risk_management']
        self.session_config = config['session_control']

        # State tracking
        self.initial_capital = config['trading']['initial_capital']
        self.current_capital = self.initial_capital
        self.daily_trades = 0
        self.consecutive_losses = 0
        self.last_trade_date = None
        self.daily_pnl = 0.0
        self.total_pnl = 0.0
        self.open_positions = 0
        self.loss_streak_cooldown_until = None

        logger.info("🛡️ Risk Manager initialized with strict limits")
        self._log_limits()

    def _log_limits(self):
        """Log all risk limits on startup"""
        logger.info("=" * 60)
        logger.info("RISK MANAGEMENT LIMITS (HARD LIMITS - NO OVERRIDE)")
        logger.info("=" * 60)
        logger.info(f"Max Risk Per Trade: {self.config['max_portfolio_risk_per_trade']}%")
        logger.info(f"Max Daily Drawdown: {self.config['max_daily_drawdown']}%")
        logger.info(f"Max Total Drawdown: {self.config['max_total_drawdown']}%")
        logger.info(f"Max Concurrent Positions: {self.config['max_concurrent_positions']}")
        logger.info(f"Max Leverage: {self.config['max_leverage']}x")
        logger.info(f"Max Stop Loss: {self.config['max_stop_loss_percent']}%")
        logger.info(f"Min Risk:Reward: 1:{self.config['min_risk_reward_ratio']}")
        logger.info(f"Max Trades Per Day: {self.session_config['max_trades_per_day']}")
        logger.info("=" * 60)

    def reset_daily_stats(self):
        """Reset daily statistics at start of new day"""
        today = datetime.now().date()
        if self.last_trade_date != today:
            logger.info(f"📅 New trading day - resetting daily stats")
            self.daily_trades = 0
            self.daily_pnl = 0.0
            self.last_trade_date = today

    def calculate_position_size(
        self,
        entry_price: float,
        stop_loss_price: float,
        leverage: int = 5
    ) -> Optional[PositionSize]:
        """
        Calculate position size based on risk parameters

        Args:
            entry_price: Entry price
            stop_loss_price: Stop loss price
            leverage: Desired leverage (will be capped at max)

        Returns:
            PositionSize object or None if invalid
        """
        # Cap leverage at maximum
        leverage = min(leverage, self.config['max_leverage'])

        # Calculate stop loss distance
        sl_distance_percent = abs(entry_price - stop_loss_price) / entry_price * 100

        # Validate stop loss distance
        if sl_distance_percent > self.config['max_stop_loss_percent']:
            logger.error(f"❌ Stop loss too wide: {sl_distance_percent:.2f}% > {self.config['max_stop_loss_percent']}%")
            return None

        if sl_distance_percent < 0.1:
            logger.error(f"❌ Stop loss too tight: {sl_distance_percent:.2f}%")
            return None

        # Calculate risk amount in USD
        max_risk_usd = self.current_capital * (self.config['max_portfolio_risk_per_trade'] / 100)

        # Calculate position size
        # Risk = Position Size * SL Distance
        # Position Size = Risk / SL Distance
        position_value_usd = (max_risk_usd / sl_distance_percent) * 100

        # Apply position size limits
        max_position_value = self.current_capital * (self.config['max_position_size'] / 100)
        position_value_usd = min(position_value_usd, max_position_value)

        # Check minimum position size
        if position_value_usd < self.config['min_position_size']:
            logger.error(f"❌ Position size too small: ${position_value_usd:.2f} < ${self.config['min_position_size']}")
            return None

        # Calculate amount in base currency (BTC)
        amount = position_value_usd / entry_price

        return PositionSize(
            amount=amount,
            value_usd=position_value_usd,
            leverage=leverage,
            risk_usd=max_risk_usd,
            risk_percent=self.config['max_portfolio_risk_per_trade']
        )

    def validate_trade(
        self,
        direction: str,
        entry_price: float,
        stop_loss_price: float,
        take_profit_prices: list,
        leverage: int
    ) -> TradeValidation:
        """
        Comprehensive pre-trade validation

        This is the CRITICAL safety check before ANY trade execution.
        Returns validation result with specific failed checks.
        """
        failed_checks = []

        # Reset daily stats if new day
        self.reset_daily_stats()

        # 1. Check if stop loss exists
        if stop_loss_price is None or stop_loss_price <= 0:
            failed_checks.append("no_stop_loss")
            return TradeValidation(
                is_valid=False,
                message="❌ CRITICAL: Stop loss is mandatory for every trade",
                failed_checks=failed_checks
            )

        # 2. Check leverage limit
        if leverage > self.config['max_leverage']:
            failed_checks.append("leverage_too_high")
            return TradeValidation(
                is_valid=False,
                message=f"❌ Leverage {leverage}x exceeds maximum {self.config['max_leverage']}x",
                failed_checks=failed_checks
            )

        # 3. Check stop loss distance
        sl_distance_percent = abs(entry_price - stop_loss_price) / entry_price * 100
        if sl_distance_percent > self.config['max_stop_loss_percent']:
            failed_checks.append("stop_loss_too_wide")
            return TradeValidation(
                is_valid=False,
                message=f"❌ Stop loss {sl_distance_percent:.2f}% exceeds max {self.config['max_stop_loss_percent']}%",
                failed_checks=failed_checks
            )

        # 4. Check Risk:Reward ratio
        if take_profit_prices and len(take_profit_prices) > 0:
            tp1_distance = abs(take_profit_prices[0] - entry_price)
            sl_distance = abs(entry_price - stop_loss_price)
            rr_ratio = tp1_distance / sl_distance if sl_distance > 0 else 0

            if rr_ratio < self.config['min_risk_reward_ratio']:
                failed_checks.append("poor_risk_reward")
                return TradeValidation(
                    is_valid=False,
                    message=f"❌ R:R {rr_ratio:.2f} below minimum {self.config['min_risk_reward_ratio']}",
                    failed_checks=failed_checks
                )

        # 5. Check daily drawdown limit
        daily_dd_percent = (self.daily_pnl / self.initial_capital) * 100
        if daily_dd_percent < -self.config['max_daily_drawdown']:
            failed_checks.append("daily_drawdown_exceeded")
            return TradeValidation(
                is_valid=False,
                message=f"🛑 CRITICAL: Daily drawdown {daily_dd_percent:.2f}% exceeds limit {self.config['max_daily_drawdown']}%",
                failed_checks=failed_checks
            )

        # 6. Check total drawdown limit
        total_dd_percent = ((self.current_capital - self.initial_capital) / self.initial_capital) * 100
        if total_dd_percent < -self.config['max_total_drawdown']:
            failed_checks.append("total_drawdown_exceeded")
            return TradeValidation(
                is_valid=False,
                message=f"🛑 CRITICAL: Total drawdown {total_dd_percent:.2f}% exceeds limit {self.config['max_total_drawdown']}%",
                failed_checks=failed_checks
            )

        # 7. Check concurrent positions limit
        if self.open_positions >= self.config['max_concurrent_positions']:
            failed_checks.append("max_positions_reached")
            return TradeValidation(
                is_valid=False,
                message=f"⚠️ Max concurrent positions reached ({self.config['max_concurrent_positions']})",
                failed_checks=failed_checks
            )

        # 8. Check daily trade limit
        if self.daily_trades >= self.session_config['max_trades_per_day']:
            failed_checks.append("daily_trade_limit")
            return TradeValidation(
                is_valid=False,
                message=f"⚠️ Daily trade limit reached ({self.session_config['max_trades_per_day']})",
                failed_checks=failed_checks
            )

        # 9. Check consecutive losses and cooldown
        if self.consecutive_losses >= self.session_config['max_consecutive_losses']:
            if self.loss_streak_cooldown_until is None:
                # Start cooldown
                self.loss_streak_cooldown_until = datetime.now() + timedelta(
                    seconds=self.session_config['cooldown_after_loss_streak']
                )
                logger.warning(f"⏸️ Loss streak detected. Cooldown until {self.loss_streak_cooldown_until}")

            if datetime.now() < self.loss_streak_cooldown_until:
                failed_checks.append("loss_streak_cooldown")
                remaining = (self.loss_streak_cooldown_until - datetime.now()).total_seconds() / 3600
                return TradeValidation(
                    is_valid=False,
                    message=f"⏸️ Cooldown active after {self.consecutive_losses} losses. {remaining:.1f}h remaining",
                    failed_checks=failed_checks
                )
            else:
                # Cooldown expired, reset
                self.consecutive_losses = 0
                self.loss_streak_cooldown_until = None
                logger.info("✅ Cooldown period ended. Resetting loss streak.")

        # All checks passed
        return TradeValidation(
            is_valid=True,
            message="✅ All risk checks passed",
            failed_checks=[]
        )

    def update_position_opened(self, position_value_usd: float):
        """Update state after opening position"""
        self.open_positions += 1
        self.daily_trades += 1
        logger.info(f"📊 Position opened. Open: {self.open_positions}, Daily trades: {self.daily_trades}")

    def update_position_closed(self, pnl_usd: float):
        """Update state after closing position"""
        self.open_positions = max(0, self.open_positions - 1)
        self.current_capital += pnl_usd
        self.daily_pnl += pnl_usd
        self.total_pnl += pnl_usd

        # Update consecutive losses
        if pnl_usd < 0:
            self.consecutive_losses += 1
            logger.warning(f"❌ Loss recorded. Consecutive losses: {self.consecutive_losses}")
        else:
            self.consecutive_losses = 0
            self.loss_streak_cooldown_until = None
            logger.info(f"✅ Win recorded. Consecutive losses reset.")

        # Calculate percentages
        daily_dd_pct = (self.daily_pnl / self.initial_capital) * 100
        total_dd_pct = ((self.current_capital - self.initial_capital) / self.initial_capital) * 100

        logger.info(f"💰 Capital: ${self.current_capital:.2f} | Daily: {daily_dd_pct:.2f}% | Total: {total_dd_pct:.2f}%")

    def get_stats(self) -> Dict:
        """Get current risk statistics"""
        daily_dd_pct = (self.daily_pnl / self.initial_capital) * 100
        total_dd_pct = ((self.current_capital - self.initial_capital) / self.initial_capital) * 100

        return {
            'current_capital': self.current_capital,
            'daily_trades': self.daily_trades,
            'daily_pnl': self.daily_pnl,
            'daily_pnl_percent': daily_dd_pct,
            'total_pnl': self.total_pnl,
            'total_pnl_percent': total_dd_pct,
            'open_positions': self.open_positions,
            'consecutive_losses': self.consecutive_losses,
            'in_cooldown': self.loss_streak_cooldown_until is not None and datetime.now() < self.loss_streak_cooldown_until
        }

    def check_override_attempt(self, action: str) -> Tuple[bool, str]:
        """
        Check if an action is prohibited

        Returns:
            (is_prohibited, response_message)
        """
        prohibited = [
            "trade_without_stop_loss",
            "leverage_above_10x",
            "risk_above_2_percent",
            "override_daily_drawdown",
            "trade_during_loss_streak",
            "all_in_position",
            "martingale_averaging",
            "trade_unstable_connection"
        ]

        if action in prohibited:
            response = "Safety rule ini tidak bisa di-override. Rule ini melindungi capital Anda dari catastrophic loss."
            logger.error(f"🚫 Override attempt blocked: {action}")
            return True, response

        return False, ""
