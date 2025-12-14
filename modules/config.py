"""
Trading Bot Configuration
Semua boundary dan risk parameters didefinisikan di sini
JANGAN OVERRIDE NILAI-NILAI INI SECARA MANUAL
"""

from dataclasses import dataclass
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

# ===========================================
# API CREDENTIALS
# ===========================================
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET", "")
BINANCE_TESTNET = os.getenv("BINANCE_TESTNET", "true").lower() == "true"

# Testnet URLs
TESTNET_BASE_URL = "https://testnet.binancefuture.com"
TESTNET_WS_URL = "wss://stream.binancefuture.com"

# Production URLs
PROD_BASE_URL = "https://fapi.binance.com"
PROD_WS_URL = "wss://fstream.binance.com"

# ===========================================
# HARD LIMITS - TIDAK BOLEH DILANGGAR
# ===========================================
@dataclass(frozen=True)
class RiskLimits:
    """Immutable risk limits - cannot be changed at runtime"""
    MAX_RISK_PER_TRADE: float = 0.01          # 1% max loss per trade
    MAX_DAILY_DRAWDOWN: float = 0.05          # 5% max daily loss
    MAX_TOTAL_DRAWDOWN: float = 0.15          # 15% max total loss
    MAX_CONCURRENT_POSITIONS: int = 3          # Max open positions
    MAX_LEVERAGE: int = 10                     # Max leverage allowed
    MAX_POSITION_SIZE_PERCENT: float = 0.10   # 10% max per position
    MAX_STOP_LOSS_PERCENT: float = 0.02       # 2% max SL
    MIN_RISK_REWARD_RATIO: float = 1.5        # Minimum R:R
    MAX_TRADES_PER_DAY: int = 10              # Max trades daily
    MAX_CONSECUTIVE_LOSSES: int = 3           # Stop after 3 losses
    COOLDOWN_AFTER_LOSSES_MINUTES: int = 240  # 4 hour cooldown

RISK_LIMITS = RiskLimits()

# ===========================================
# SCALPING STRATEGY PARAMETERS
# ===========================================
@dataclass
class ScalpingConfig:
    """Scalping strategy configuration"""
    # Timeframes
    PRIMARY_TIMEFRAME: str = "5m"
    HIGHER_TIMEFRAME: str = "15m"
    TREND_TIMEFRAME: str = "1h"

    # Indicators
    EMA_FAST: int = 9
    EMA_SLOW: int = 21
    EMA_TREND: int = 50
    RSI_PERIOD: int = 14
    RSI_OVERBOUGHT: int = 70
    RSI_OVERSOLD: int = 30
    ATR_PERIOD: int = 14
    ATR_MULTIPLIER_SL: float = 1.5
    ATR_MULTIPLIER_TP: float = 2.5
    VOLUME_MA_PERIOD: int = 20
    VOLUME_THRESHOLD: float = 1.2  # 120% of average

    # Entry conditions
    MIN_CONFIRMATIONS: int = 4
    MAX_SPREAD_PERCENT: float = 0.05  # 0.05% max spread

    # Take profit levels (partial exits)
    TP_LEVELS: List[float] = None
    TP_PERCENTAGES: List[float] = None

    def __post_init__(self):
        self.TP_LEVELS = [1.5, 2.0, 3.0]  # R:R ratios
        self.TP_PERCENTAGES = [0.5, 0.3, 0.2]  # 50%, 30%, 20%

SCALPING_CONFIG = ScalpingConfig()

# ===========================================
# TRADING PAIRS
# ===========================================
ALLOWED_PAIRS = [
    "BTCUSDT",
    "ETHUSDT",
    "BNBUSDT",
    "SOLUSDT",
    "XRPUSDT",
]

# ===========================================
# BLACKOUT PERIODS (no trading)
# ===========================================
BLACKOUT_EVENTS = [
    "FOMC",
    "CPI",
    "NFP",
    "GDP",
]

# Minutes before/after news to avoid trading
NEWS_BUFFER_MINUTES = 30

# ===========================================
# LOGGING
# ===========================================
LOG_LEVEL = "INFO"
LOG_FILE = "trading_bot.log"
TRADE_LOG_FILE = "trades.json"

# ===========================================
# TELEGRAM NOTIFICATIONS (optional)
# ===========================================
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
ENABLE_TELEGRAM = bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)
