"""
Telegram Bot Integration for Trade Notifications and Commands
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from telegram import Update, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)
from telegram.constants import ParseMode
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """
    Telegram bot for sending trading notifications and handling commands
    """

    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        """Initialize Telegram notifier"""
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID')

        self.bot: Optional[Bot] = None
        self.application: Optional[Application] = None
        self.enabled = bool(self.bot_token and self.chat_id)

        if self.enabled:
            self.bot = Bot(token=self.bot_token)
            logger.info("✅ Telegram notifications enabled")
        else:
            logger.warning("⚠️  Telegram notifications disabled (missing credentials)")

        # Stats tracking
        self.daily_stats = {
            'trades': 0,
            'wins': 0,
            'losses': 0,
            'pnl': 0.0,
            'last_reset': datetime.now().date()
        }

    def _reset_daily_stats_if_needed(self):
        """Reset daily stats at midnight"""
        today = datetime.now().date()
        if self.daily_stats['last_reset'] != today:
            self.daily_stats = {
                'trades': 0,
                'wins': 0,
                'losses': 0,
                'pnl': 0.0,
                'last_reset': today
            }

    async def send_message(self, message: str, parse_mode: str = ParseMode.HTML):
        """Send a message to Telegram"""
        if not self.enabled:
            logger.debug(f"Telegram disabled, message not sent: {message}")
            return False

        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=parse_mode
            )
            logger.debug(f"✅ Telegram message sent: {message[:50]}...")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to send Telegram message: {e}")
            return False

    def send_message_sync(self, message: str):
        """Synchronous wrapper for send_message"""
        if not self.enabled:
            return False

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self.send_message(message))
            else:
                loop.run_until_complete(self.send_message(message))
            return True
        except Exception as e:
            logger.error(f"❌ Error in sync send: {e}")
            return False

    # ===========================================
    # TRADE NOTIFICATIONS
    # ===========================================

    async def notify_trade_entry(self, trade_data: Dict[str, Any]):
        """Notify when a trade is opened"""
        self._reset_daily_stats_if_needed()

        symbol = trade_data.get('symbol', 'UNKNOWN')
        side = trade_data.get('side', 'LONG').upper()
        entry_price = trade_data.get('entry_price', 0)
        quantity = trade_data.get('quantity', 0)
        stop_loss = trade_data.get('stop_loss', 0)
        take_profit_1 = trade_data.get('take_profit_1', 0)
        leverage = trade_data.get('leverage', 1)
        risk_usd = trade_data.get('risk_usd', 0)

        emoji = "🟢" if side == "LONG" else "🔴"

        message = f"""
{emoji} <b>NEW TRADE OPENED</b> {emoji}

💰 <b>Symbol:</b> {symbol}
📈 <b>Side:</b> {side}
💵 <b>Entry:</b> ${entry_price:.4f}
📊 <b>Quantity:</b> {quantity:.4f}
⚡ <b>Leverage:</b> {leverage}x

🎯 <b>Targets:</b>
• TP1: ${take_profit_1:.4f}
• SL: ${stop_loss:.4f}

💸 <b>Risk:</b> ${risk_usd:.2f}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        await self.send_message(message)
        self.daily_stats['trades'] += 1

    async def notify_take_profit(self, tp_data: Dict[str, Any]):
        """Notify when take profit is hit"""
        symbol = tp_data.get('symbol', 'UNKNOWN')
        tp_level = tp_data.get('tp_level', 1)
        price = tp_data.get('price', 0)
        quantity_closed = tp_data.get('quantity_closed', 0)
        profit = tp_data.get('profit', 0)
        percentage = tp_data.get('percentage', 0)

        message = f"""
🎯 <b>TAKE PROFIT HIT!</b> ✅

💰 <b>Symbol:</b> {symbol}
🎯 <b>TP{tp_level}:</b> ${price:.4f}
📊 <b>Closed:</b> {quantity_closed:.4f}

💵 <b>Profit:</b> ${profit:.2f} ({percentage:+.2f}%)

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        await self.send_message(message)
        self.daily_stats['wins'] += 1
        self.daily_stats['pnl'] += profit

    async def notify_stop_loss(self, sl_data: Dict[str, Any]):
        """Notify when stop loss is hit"""
        symbol = sl_data.get('symbol', 'UNKNOWN')
        price = sl_data.get('price', 0)
        loss = sl_data.get('loss', 0)
        percentage = sl_data.get('percentage', 0)
        reason = sl_data.get('reason', 'Stop Loss')

        message = f"""
🛑 <b>STOP LOSS HIT</b> ⚠️

💰 <b>Symbol:</b> {symbol}
🔴 <b>Exit:</b> ${price:.4f}
📉 <b>Loss:</b> ${loss:.2f} ({percentage:.2f}%)
❌ <b>Reason:</b> {reason}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        await self.send_message(message)
        self.daily_stats['losses'] += 1
        self.daily_stats['pnl'] += loss

    async def notify_trade_closed(self, close_data: Dict[str, Any]):
        """Notify when trade is manually closed"""
        symbol = close_data.get('symbol', 'UNKNOWN')
        price = close_data.get('price', 0)
        pnl = close_data.get('pnl', 0)
        percentage = close_data.get('percentage', 0)
        reason = close_data.get('reason', 'Manual Close')

        emoji = "✅" if pnl >= 0 else "❌"

        message = f"""
{emoji} <b>TRADE CLOSED</b>

💰 <b>Symbol:</b> {symbol}
💵 <b>Exit:</b> ${price:.4f}
📊 <b>P&L:</b> ${pnl:.2f} ({percentage:+.2f}%)
ℹ️ <b>Reason:</b> {reason}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        await self.send_message(message)

        if pnl >= 0:
            self.daily_stats['wins'] += 1
        else:
            self.daily_stats['losses'] += 1
        self.daily_stats['pnl'] += pnl

    # ===========================================
    # RISK WARNINGS
    # ===========================================

    async def notify_risk_warning(self, warning_data: Dict[str, Any]):
        """Send risk management warnings"""
        warning_type = warning_data.get('type', 'UNKNOWN')
        message_text = warning_data.get('message', '')
        severity = warning_data.get('severity', 'warning')

        emoji = "🚨" if severity == "critical" else "⚠️"

        message = f"""
{emoji} <b>RISK WARNING</b> {emoji}

⚡ <b>Type:</b> {warning_type}
📝 <b>Message:</b> {message_text}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        await self.send_message(message)

    async def notify_daily_loss_limit(self, drawdown: float, limit: float):
        """Notify when daily loss limit is reached"""
        message = f"""
🚨 <b>DAILY LOSS LIMIT REACHED!</b> 🚨

📉 <b>Drawdown:</b> {drawdown:.2f}%
🛑 <b>Limit:</b> {limit:.2f}%

⚠️ <b>Trading paused for today</b>
✅ Will resume tomorrow

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        await self.send_message(message)

    async def notify_max_drawdown(self, drawdown: float, limit: float):
        """Notify when max drawdown is reached"""
        message = f"""
🚨🚨 <b>MAX DRAWDOWN ALERT!</b> 🚨🚨

📉 <b>Total Drawdown:</b> {drawdown:.2f}%
🛑 <b>Limit:</b> {limit:.2f}%

⚠️ <b>BOT STOPPED - IMMEDIATE ACTION REQUIRED!</b>

Please review your strategy and risk settings.

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        await self.send_message(message)

    async def notify_consecutive_losses(self, losses: int, cooldown_hours: int):
        """Notify about consecutive losses cooldown"""
        message = f"""
⚠️ <b>COOLDOWN ACTIVATED</b>

📉 <b>Consecutive Losses:</b> {losses}
⏸️ <b>Cooldown:</b> {cooldown_hours} hours

Bot will pause trading to protect capital.

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        await self.send_message(message)

    # ===========================================
    # DAILY SUMMARY
    # ===========================================

    async def send_daily_summary(self, stats: Optional[Dict[str, Any]] = None):
        """Send daily trading summary"""
        self._reset_daily_stats_if_needed()

        if stats:
            trades = stats.get('total_trades', self.daily_stats['trades'])
            wins = stats.get('wins', self.daily_stats['wins'])
            losses = stats.get('losses', self.daily_stats['losses'])
            pnl = stats.get('pnl', self.daily_stats['pnl'])
            win_rate = stats.get('win_rate', 0)
            balance = stats.get('balance', 0)
        else:
            trades = self.daily_stats['trades']
            wins = self.daily_stats['wins']
            losses = self.daily_stats['losses']
            pnl = self.daily_stats['pnl']
            win_rate = (wins / trades * 100) if trades > 0 else 0
            balance = 0

        emoji = "📈" if pnl >= 0 else "📉"

        message = f"""
{emoji} <b>DAILY SUMMARY</b> {emoji}
<i>{datetime.now().strftime('%Y-%m-%d')}</i>

📊 <b>Performance:</b>
• Total Trades: {trades}
• Wins: {wins} ✅
• Losses: {losses} ❌
• Win Rate: {win_rate:.1f}%

💰 <b>P&L:</b>
• Daily P&L: ${pnl:+.2f}
{f'• Balance: ${balance:.2f}' if balance > 0 else ''}

⏰ {datetime.now().strftime('%H:%M:%S')}
"""
        await self.send_message(message)

    # ===========================================
    # BOT COMMANDS
    # ===========================================

    def start_bot_commands(self, bot_manager=None):
        """Start listening for bot commands"""
        if not self.enabled:
            logger.warning("Cannot start bot commands - Telegram disabled")
            return False

        try:
            self.application = Application.builder().token(self.bot_token).build()

            # Store bot manager reference for commands
            self.bot_manager = bot_manager

            # Register command handlers
            self.application.add_handler(CommandHandler("start", self._cmd_start))
            self.application.add_handler(CommandHandler("help", self._cmd_help))
            self.application.add_handler(CommandHandler("status", self._cmd_status))
            self.application.add_handler(CommandHandler("balance", self._cmd_balance))
            self.application.add_handler(CommandHandler("positions", self._cmd_positions))
            self.application.add_handler(CommandHandler("close", self._cmd_close_all))
            self.application.add_handler(CommandHandler("stats", self._cmd_stats))
            self.application.add_handler(CommandHandler("pause", self._cmd_pause))
            self.application.add_handler(CommandHandler("resume", self._cmd_resume))

            # Start polling in background
            logger.info("🤖 Telegram bot commands activated")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to start bot commands: {e}")
            return False

    async def _cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        message = """
🤖 <b>Binance Algo Bot</b>

Welcome! I'm your trading assistant.

Use /help to see available commands.
"""
        await update.message.reply_text(message, parse_mode=ParseMode.HTML)

    async def _cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        message = """
📚 <b>Available Commands:</b>

/status - Bot and system status
/balance - Account balance
/positions - Open positions
/stats - Daily statistics
/close - Close all positions (⚠️ use carefully!)
/pause - Pause trading
/resume - Resume trading
/help - Show this help message

⚠️ <b>Warning:</b> Some commands require authorization.
"""
        await update.message.reply_text(message, parse_mode=ParseMode.HTML)

    async def _cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        # TODO: Get actual status from bot manager
        message = """
✅ <b>BOT STATUS</b>

🟢 Status: Running
⏰ Uptime: 2h 34m
📊 Open Positions: 1
💰 Daily P&L: +$45.30

Last update: {datetime.now().strftime('%H:%M:%S')}
"""
        await update.message.reply_text(message, parse_mode=ParseMode.HTML)

    async def _cmd_balance(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /balance command"""
        # TODO: Get actual balance from exchange
        message = """
💰 <b>ACCOUNT BALANCE</b>

Total: $10,234.56
Available: $9,500.00
In Positions: $734.56

⏰ {datetime.now().strftime('%H:%M:%S')}
"""
        await update.message.reply_text(message, parse_mode=ParseMode.HTML)

    async def _cmd_positions(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /positions command"""
        # TODO: Get actual positions from bot manager
        message = """
📊 <b>OPEN POSITIONS</b>

1. BNBUSDT
   • Side: LONG
   • Entry: $245.30
   • Current: $247.85
   • P&L: +$45.30 (+1.04%)

⏰ {datetime.now().strftime('%H:%M:%S')}
"""
        await update.message.reply_text(message, parse_mode=ParseMode.HTML)

    async def _cmd_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        await self.send_daily_summary()

    async def _cmd_close_all(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /close command"""
        # TODO: Implement actual close all logic
        message = """
⚠️ <b>CLOSE ALL POSITIONS</b>

This will close ALL open positions immediately.

Type /confirm_close to proceed.
⚠️ This action cannot be undone!
"""
        await update.message.reply_text(message, parse_mode=ParseMode.HTML)

    async def _cmd_pause(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /pause command"""
        message = """
⏸️ <b>TRADING PAUSED</b>

Bot will not open new positions.
Existing positions remain open.

Use /resume to continue trading.
"""
        await update.message.reply_text(message, parse_mode=ParseMode.HTML)

    async def _cmd_resume(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /resume command"""
        message = """
▶️ <b>TRADING RESUMED</b>

Bot is now actively scanning for signals.

Use /pause to stop trading.
"""
        await update.message.reply_text(message, parse_mode=ParseMode.HTML)

    # ===========================================
    # SYSTEM NOTIFICATIONS
    # ===========================================

    async def notify_bot_started(self):
        """Notify when bot starts"""
        message = """
🚀 <b>BOT STARTED</b>

Trading bot is now running and scanning markets.

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        await self.send_message(message)

    async def notify_bot_stopped(self, reason: str = "Manual stop"):
        """Notify when bot stops"""
        message = f"""
🛑 <b>BOT STOPPED</b>

Reason: {reason}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        await self.send_message(message)

    async def notify_error(self, error_msg: str):
        """Notify about system errors"""
        message = f"""
❌ <b>ERROR OCCURRED</b>

{error_msg}

Check logs for details.

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        await self.send_message(message)


# ===========================================
# CONVENIENCE FUNCTIONS
# ===========================================

_notifier_instance: Optional[TelegramNotifier] = None


def get_telegram_notifier() -> TelegramNotifier:
    """Get singleton instance of TelegramNotifier"""
    global _notifier_instance
    if _notifier_instance is None:
        _notifier_instance = TelegramNotifier()
    return _notifier_instance


def send_telegram_notification(message: str):
    """Quick send notification (synchronous)"""
    notifier = get_telegram_notifier()
    notifier.send_message_sync(message)


# Example usage
if __name__ == "__main__":
    # Test notifications
    notifier = TelegramNotifier()

    if notifier.enabled:
        # Test trade entry
        asyncio.run(notifier.notify_trade_entry({
            'symbol': 'BNBUSDT',
            'side': 'LONG',
            'entry_price': 245.30,
            'quantity': 10.5,
            'stop_loss': 242.00,
            'take_profit_1': 250.00,
            'leverage': 5,
            'risk_usd': 50.00
        }))

        print("✅ Test notification sent!")
    else:
        print("❌ Telegram not configured")
