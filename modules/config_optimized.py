"""
Trading Bot Configuration - OPTIMIZED VERSION
Risk parameters yang sudah di-tune untuk minimize SL hits
dan maximize profit dengan dynamic stop loss
"""

from dataclasses import dataclass, field
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
# HARD LIMITS - SAFETY BOUNDARIES
# ===========================================
@dataclass(frozen=True)
class RiskLimits:
    """Immutable risk limits - safety net"""
    MAX_RISK_PER_TRADE: float = 0.015         # 1.5% max loss per trade (sedikit lebih longgar)
    MAX_DAILY_DRAWDOWN: float = 0.06          # 6% max daily loss
    MAX_TOTAL_DRAWDOWN: float = 0.18          # 18% max total loss
    MAX_CONCURRENT_POSITIONS: int = 3          # Max open positions
    MAX_LEVERAGE: int = 10                     # Max leverage allowed
    MAX_POSITION_SIZE_PERCENT: float = 0.12   # 12% max per position
    MAX_STOP_LOSS_PERCENT: float = 0.035      # 3.5% max SL (ATR-based bisa sampai sini)
    MIN_RISK_REWARD_RATIO: float = 1.8        # Higher R:R untuk kompensasi wider SL
    MAX_TRADES_PER_DAY: int = 8               # Kurangi frekuensi, tingkatkan kualitas
    MAX_CONSECUTIVE_LOSSES: int = 3           # Stop after 3 losses
    COOLDOWN_AFTER_LOSSES_MINUTES: int = 180  # 3 hour cooldown

RISK_LIMITS = RiskLimits()

# ===========================================
# OPTIMIZED SCALPING PARAMETERS
# ===========================================
@dataclass
class ScalpingConfig:
    """
    Scalping strategy configuration - OPTIMIZED
    Focus: Better entries, dynamic SL, smart exits
    """
    # Timeframes - gunakan timeframe lebih tinggi untuk filter
    PRIMARY_TIMEFRAME: str = "5m"
    HIGHER_TIMEFRAME: str = "15m"
    TREND_TIMEFRAME: str = "1h"
    STRUCTURE_TIMEFRAME: str = "4h"  # Tambah untuk market structure

    # EMA Settings - optimized crossover
    EMA_FAST: int = 8               # Lebih responsif
    EMA_SLOW: int = 21
    EMA_TREND: int = 50
    EMA_STRUCTURE: int = 200        # Major trend filter

    # RSI - wider range untuk avoid false signals
    RSI_PERIOD: int = 14
    RSI_OVERBOUGHT: int = 75        # Naikkan threshold
    RSI_OVERSOLD: int = 25          # Turunkan threshold
    RSI_NEUTRAL_HIGH: int = 60      # Zone netral atas
    RSI_NEUTRAL_LOW: int = 40       # Zone netral bawah

    # ATR for Dynamic SL/TP - KEY OPTIMIZATION
    ATR_PERIOD: int = 14
    ATR_MULTIPLIER_SL: float = 2.0           # SL = 2x ATR (lebih lebar)
    ATR_MULTIPLIER_SL_MIN: float = 1.5       # Minimum 1.5x ATR
    ATR_MULTIPLIER_SL_MAX: float = 2.5       # Maximum 2.5x ATR
    ATR_MULTIPLIER_TP1: float = 2.5          # TP1 = 2.5x ATR
    ATR_MULTIPLIER_TP2: float = 4.0          # TP2 = 4x ATR
    ATR_MULTIPLIER_TP3: float = 6.0          # TP3 = 6x ATR (runner)

    # Volume confirmation
    VOLUME_MA_PERIOD: int = 20
    VOLUME_THRESHOLD: float = 1.3            # 130% volume untuk konfirmasi
    VOLUME_SPIKE_THRESHOLD: float = 2.5      # Avoid entry saat volume spike

    # Volatility filter - PENTING
    ATR_VOLATILITY_PERIOD: int = 50          # Longer period untuk baseline
    VOLATILITY_MIN_RATIO: float = 0.6        # Skip jika ATR < 60% average
    VOLATILITY_MAX_RATIO: float = 2.0        # Skip jika ATR > 200% average

    # Entry conditions - MORE SELECTIVE
    MIN_CONFIRMATIONS: int = 5               # Naikkan dari 4 ke 5
    MAX_SPREAD_PERCENT: float = 0.04         # Lebih ketat spread

    # Pullback entry settings
    PULLBACK_ENABLED: bool = True
    PULLBACK_MIN_PERCENT: float = 0.3        # Min 0.3% pullback
    PULLBACK_MAX_PERCENT: float = 1.5        # Max 1.5% pullback
    PULLBACK_EMA_TOUCH: bool = True          # Entry saat touch EMA

    # Take profit levels - OPTIMIZED untuk wider SL
    TP_LEVELS: List[float] = field(default_factory=list)
    TP_PERCENTAGES: List[float] = field(default_factory=list)

    # Trailing stop settings - SMART TRAILING
    TRAILING_ENABLED: bool = True
    TRAILING_ACTIVATION_RR: float = 1.0      # Aktifkan setelah 1R profit
    TRAILING_CALLBACK_PERCENT: float = 0.4   # 0.4% callback rate
    TRAILING_STEP_PERCENT: float = 0.2       # Step 0.2%

    # Breakeven settings
    BREAKEVEN_ENABLED: bool = True
    BREAKEVEN_ACTIVATION_RR: float = 0.7     # Move to BE setelah 0.7R
    BREAKEVEN_BUFFER_PERCENT: float = 0.1    # Buffer 0.1% above entry

    # Time-based filters
    AVOID_FIRST_CANDLE_MINUTES: int = 5      # Skip 5 menit pertama candle baru
    MAX_HOLD_TIME_MINUTES: int = 240         # Max hold 4 jam untuk scalp

    # Session filters (UTC hours)
    PREFERRED_SESSIONS: List[tuple] = field(default_factory=list)
    AVOID_SESSIONS: List[tuple] = field(default_factory=list)

    def __post_init__(self):
        # TP levels dengan R:R yang lebih tinggi
        self.TP_LEVELS = [1.8, 3.0, 5.0]     # Target R:R lebih tinggi
        self.TP_PERCENTAGES = [0.40, 0.35, 0.25]  # 40%, 35%, 25%

        # Trading sessions (UTC) - London & NY overlap best
        self.PREFERRED_SESSIONS = [
            (7, 10),   # London open
            (13, 17),  # NY open / London-NY overlap
            (20, 23),  # Asian pre-market volatility
        ]
        self.AVOID_SESSIONS = [
            (4, 6),    # Dead zone
            (23, 2),   # Low liquidity
        ]

SCALPING_CONFIG = ScalpingConfig()

# ===========================================
# MARKET CONDITION PROFILES
# ===========================================
@dataclass
class MarketProfile:
    """Adjust parameters based on market conditions"""
    name: str
    atr_multiplier_sl: float
    atr_multiplier_tp: float
    min_confirmations: int
    trailing_callback: float

# Pre-defined profiles
MARKET_PROFILES = {
    "LOW_VOLATILITY": MarketProfile(
        name="Low Volatility",
        atr_multiplier_sl=1.5,
        atr_multiplier_tp=2.5,
        min_confirmations=4,
        trailing_callback=0.3
    ),
    "NORMAL": MarketProfile(
        name="Normal",
        atr_multiplier_sl=2.0,
        atr_multiplier_tp=3.0,
        min_confirmations=5,
        trailing_callback=0.4
    ),
    "HIGH_VOLATILITY": MarketProfile(
        name="High Volatility",
        atr_multiplier_sl=2.5,
        atr_multiplier_tp=4.0,
        min_confirmations=6,
        trailing_callback=0.6
    ),
}

# ===========================================
# TRADING PAIRS
# ===========================================
# BNB sebagai primary - backed by Binance, lebih stabil
# BTC/ETH sebagai secondary untuk diversifikasi
ALLOWED_PAIRS = [
    "BNBUSDT",   # PRIMARY - Binance native, stable, good trends
    "BTCUSDT",   # SECONDARY - market leader
    "ETHUSDT",   # TERTIARY - good volatility
]

# Pair-specific settings - BNB OPTIMIZED
PAIR_CONFIGS = {
    "BNBUSDT": {
        "priority": 1,
        "max_leverage": 8,
        "sl_multiplier": 1.0,        # Tighter SL - BNB lebih stabil
        "tp_multiplier": 0.9,        # Slightly tighter TP, faster profit
        "min_volume_ratio": 0.8,     # BNB volume konsisten
        "atr_period": 14,
        "preferred": True,
        "notes": "Primary pair - Binance backing, stable trends"
    },
    "BTCUSDT": {
        "priority": 2,
        "max_leverage": 5,           # BTC volatile
        "sl_multiplier": 1.3,        # Wider SL
        "tp_multiplier": 1.2,
        "min_volume_ratio": 1.0,
        "atr_period": 14,
        "preferred": False,
        "notes": "Secondary - high liquidity but volatile"
    },
    "ETHUSDT": {
        "priority": 3,
        "max_leverage": 5,
        "sl_multiplier": 1.3,
        "tp_multiplier": 1.2,
        "min_volume_ratio": 1.0,
        "atr_period": 14,
        "preferred": False,
        "notes": "Tertiary - good for trending markets"
    },
}

# ===========================================
# BNB SPECIFIC SETTINGS
# ===========================================
BNB_CONFIG = {
    # BNB characteristics
    "typical_daily_range": 0.03,      # ~3% typical daily range
    "max_expected_move": 0.08,        # 8% max expected move
    "correlation_btc": 0.75,          # High correlation dengan BTC

    # Entry preferences untuk BNB
    "prefer_pullback_entry": True,    # BNB bagus untuk pullback
    "pullback_to_ema": 21,            # Pullback ke EMA21
    "trend_confirmation_ema": 50,     # Trend filter

    # Exit preferences
    "scale_out_enabled": True,
    "first_target_rr": 1.5,           # TP1 di 1.5R
    "runner_enabled": True,           # Keep 20% sebagai runner

    # Risk settings khusus BNB
    "max_position_percent": 0.15,     # Bisa lebih besar karena stable
    "max_leverage": 8,

    # Session preferences (UTC) - BNB best hours
    "best_hours": [1, 2, 3, 8, 9, 14, 15],  # Asian + London + NY
}

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
