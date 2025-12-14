"""
Tier Management System
Enforces freemium tier limits and feature gates
Integrates with License State for automatic tier detection
"""

import logging
from typing import Dict, Tuple, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class TierLevel(Enum):
    """Available subscription tiers"""
    FREE = "free"
    PRO = "pro"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class TierManager:
    """
    Manages tier-based feature access and limitations

    This ensures free users get value while incentivizing upgrades
    """

    def __init__(self, tier_config: Dict, user_tier: str = "free", auto_detect_license: bool = True):
        """
        Initialize Tier Manager

        Args:
            tier_config: Tier configuration dictionary
            user_tier: User tier (default: 'free')
            auto_detect_license: Automatically detect tier from activated license
        """
        # Auto-detect tier from license if enabled
        if auto_detect_license:
            try:
                from .license_state import get_license_state
                license_state = get_license_state()
                detected_tier = license_state.get_current_tier()
                if detected_tier:
                    user_tier = detected_tier
                    logger.info(f"🔑 License detected: {detected_tier.upper()}")
            except Exception as e:
                logger.warning(f"⚠️ Could not detect license tier: {e}. Using default: {user_tier}")

        self.tier_config = tier_config
        self.user_tier = TierLevel(user_tier)
        self.current_tier_config = tier_config['tiers'][user_tier]

        logger.info(f"🎫 Tier Manager initialized: {self.user_tier.value.upper()}")
        self._log_tier_features()

    def _log_tier_features(self):
        """Log user's current tier features"""
        features = self.current_tier_config['features']
        logger.info("=" * 60)
        logger.info(f"TIER: {self.current_tier_config['name']} (${self.current_tier_config['price']}/mo)")
        logger.info("=" * 60)
        logger.info(f"Live Trading: {'✅' if features['live_trading'] else '❌ (Paper Only)'}")
        logger.info(f"Max Position: ${features['max_position_size_usd']}")
        logger.info(f"Daily Trades: {features['max_daily_trades']}")
        logger.info(f"Concurrent Positions: {features['max_concurrent_positions']}")
        logger.info(f"Trading Pairs: {features['max_pairs']}")
        logger.info("=" * 60)

    def can_access_feature(self, feature: str) -> Tuple[bool, str]:
        """
        Check if user can access a feature

        Args:
            feature: Feature name to check

        Returns:
            (can_access, error_message)
        """
        feature_gates = self.tier_config['feature_gates']

        if feature in feature_gates:
            required_tier = TierLevel(feature_gates[feature]['required_tier'])

            # Check tier hierarchy: FREE < PRO < PREMIUM < ENTERPRISE
            tier_hierarchy = {
                TierLevel.FREE: 0,
                TierLevel.PRO: 1,
                TierLevel.PREMIUM: 2,
                TierLevel.ENTERPRISE: 3
            }

            if tier_hierarchy[self.user_tier] < tier_hierarchy[required_tier]:
                error_msg = feature_gates[feature]['error_message']
                logger.warning(f"🚫 Feature '{feature}' blocked: {error_msg}")
                return False, error_msg

        return True, ""

    def check_live_trading_allowed(self) -> Tuple[bool, str]:
        """Check if user can use live trading"""
        features = self.current_tier_config['features']

        if not features['live_trading']:
            msg = "Live trading requires PRO tier. Upgrade to start trading with real money! 💰"
            logger.warning(f"🚫 {msg}")
            return False, msg

        return True, ""

    def check_position_size_limit(self, position_value_usd: float) -> Tuple[bool, str]:
        """Check if position size is within tier limits"""
        features = self.current_tier_config['features']
        max_size = features['max_position_size_usd']

        # -1 means unlimited
        if max_size == -1:
            return True, ""

        if position_value_usd > max_size:
            msg = f"Position size ${position_value_usd:.0f} exceeds {self.user_tier.value.upper()} limit of ${max_size}. Upgrade for higher limits! 📈"
            logger.warning(f"🚫 {msg}")
            return False, msg

        return True, ""

    def check_daily_trades_limit(self, current_daily_trades: int) -> Tuple[bool, str]:
        """Check if daily trade limit reached"""
        features = self.current_tier_config['features']
        max_trades = features['max_daily_trades']

        # -1 means unlimited
        if max_trades == -1:
            return True, ""

        if current_daily_trades >= max_trades:
            msg = f"Daily trade limit reached ({max_trades}). Upgrade to {self.get_next_tier()} for more trades! 🚀"
            logger.warning(f"🚫 {msg}")
            return False, msg

        return True, ""

    def check_concurrent_positions_limit(self, current_positions: int) -> Tuple[bool, str]:
        """Check if concurrent positions limit reached"""
        features = self.current_tier_config['features']
        max_positions = features['max_concurrent_positions']

        # -1 means unlimited
        if max_positions == -1:
            return True, ""

        if current_positions >= max_positions:
            msg = f"Max concurrent positions reached ({max_positions}). Upgrade to manage more positions! 💪"
            logger.warning(f"🚫 {msg}")
            return False, msg

        return True, ""

    def check_trading_pair_allowed(self, pair: str) -> Tuple[bool, str]:
        """Check if trading pair is allowed in current tier"""
        features = self.current_tier_config['features']
        available_pairs = features['available_pairs']

        # "all" means all pairs allowed
        if available_pairs == "all":
            return True, ""

        if pair not in available_pairs:
            msg = f"Pair {pair} not available in {self.user_tier.value.upper()} tier. Available: {', '.join(available_pairs)}. Upgrade for more pairs! 🎯"
            logger.warning(f"🚫 {msg}")
            return False, msg

        return True, ""

    def check_leverage_allowed(self, leverage: int) -> Tuple[bool, str]:
        """Check if leverage is allowed in current tier"""
        features = self.current_tier_config['features']
        available_leverage = features['available_leverage']

        if leverage not in available_leverage:
            msg = f"Leverage {leverage}x not available in {self.user_tier.value.upper()} tier. Available: {available_leverage}. Upgrade for higher leverage! ⚡"
            logger.warning(f"🚫 {msg}")
            return False, msg

        return True, ""

    def check_strategy_allowed(self, strategy: str) -> Tuple[bool, str]:
        """Check if strategy is available in current tier"""
        features = self.current_tier_config['features']
        available_strategies = features['available_strategies']

        # "all" means all strategies allowed
        if available_strategies == "all":
            return True, ""

        if strategy not in available_strategies:
            msg = f"Strategy '{strategy}' is a PRO/PREMIUM feature. Upgrade to access advanced strategies! 🎓"
            logger.warning(f"🚫 {msg}")
            return False, msg

        return True, ""

    def get_next_tier(self) -> str:
        """Get next tier for upsell messaging"""
        if self.user_tier == TierLevel.FREE:
            return "PRO"
        elif self.user_tier == TierLevel.PRO:
            return "PREMIUM"
        elif self.user_tier == TierLevel.PREMIUM:
            return "ENTERPRISE"
        return "PREMIUM"

    def get_upsell_message(self) -> str:
        """Get tier-specific upsell message"""
        return self.current_tier_config.get('upsell_message', '')

    def get_tier_features(self) -> Dict:
        """Get all features for current tier"""
        return self.current_tier_config['features']

    def should_show_trial_offer(self) -> Tuple[bool, Dict]:
        """
        Check if should show trial offer to user

        Returns:
            (should_show, trial_config)
        """
        trials = self.tier_config['conversion']['trials']

        if self.user_tier == TierLevel.FREE:
            return True, trials['pro_trial']
        elif self.user_tier == TierLevel.PRO:
            return True, trials['premium_trial']

        return False, {}

    def log_conversion_opportunity(self, trigger: str):
        """Log conversion opportunity for analytics"""
        logger.info(f"💰 CONVERSION OPPORTUNITY: {trigger} (Current tier: {self.user_tier.value})")

        # Get appropriate trial offer
        should_show, trial = self.should_show_trial_offer()

        if should_show and trial.get('enabled'):
            next_tier = self.get_next_tier()
            logger.info(f"🎁 Trial available: {trial['duration_days']} days {next_tier} trial")

    def get_max_daily_trades(self) -> int:
        """Get maximum daily trades for current tier"""
        return self.current_tier_config['features']['max_daily_trades']

    def get_max_positions(self) -> int:
        """Get maximum concurrent positions for current tier"""
        return self.current_tier_config['features']['max_concurrent_positions']

    def get_max_position_size(self) -> float:
        """Get maximum position size in USD for current tier"""
        return self.current_tier_config['features']['max_position_size_usd']

    def get_stats(self) -> Dict:
        """Get current tier statistics"""
        features = self.current_tier_config['features']

        return {
            'tier': self.user_tier.value,
            'tier_name': self.current_tier_config['name'],
            'price': self.current_tier_config['price'],
            'live_trading_enabled': features['live_trading'],
            'max_position_size': features['max_position_size_usd'],
            'max_daily_trades': features['max_daily_trades'],
            'max_concurrent_positions': features['max_concurrent_positions'],
            'available_pairs': features['available_pairs'] if isinstance(features['available_pairs'], list) else 'all',
            'next_tier': self.get_next_tier()
        }


class TierEnforcer:
    """
    High-level tier enforcement wrapper

    Use this in main trading logic to enforce all tier limits
    """

    def __init__(self, tier_manager: TierManager, risk_manager):
        self.tier_manager = tier_manager
        self.risk_manager = risk_manager

    def validate_trade_with_tier(
        self,
        pair: str,
        position_value_usd: float,
        leverage: int,
        strategy: str,
        is_live: bool
    ) -> Tuple[bool, str]:
        """
        Comprehensive tier validation for trade

        Returns:
            (is_valid, error_message)
        """
        # Check if live trading allowed
        if is_live:
            allowed, msg = self.tier_manager.check_live_trading_allowed()
            if not allowed:
                return False, msg

        # Check position size limit
        allowed, msg = self.tier_manager.check_position_size_limit(position_value_usd)
        if not allowed:
            self.tier_manager.log_conversion_opportunity("position_size_limit_hit")
            return False, msg

        # Check daily trades limit
        daily_trades = self.risk_manager.daily_trades
        allowed, msg = self.tier_manager.check_daily_trades_limit(daily_trades)
        if not allowed:
            self.tier_manager.log_conversion_opportunity("daily_trade_limit_hit")
            return False, msg

        # Check concurrent positions
        open_positions = self.risk_manager.open_positions
        allowed, msg = self.tier_manager.check_concurrent_positions_limit(open_positions)
        if not allowed:
            self.tier_manager.log_conversion_opportunity("concurrent_positions_limit_hit")
            return False, msg

        # Check trading pair
        allowed, msg = self.tier_manager.check_trading_pair_allowed(pair)
        if not allowed:
            self.tier_manager.log_conversion_opportunity("pair_not_available")
            return False, msg

        # Check leverage
        allowed, msg = self.tier_manager.check_leverage_allowed(leverage)
        if not allowed:
            return False, msg

        # Check strategy
        allowed, msg = self.tier_manager.check_strategy_allowed(strategy)
        if not allowed:
            self.tier_manager.log_conversion_opportunity("strategy_not_available")
            return False, msg

        return True, "✅ All tier checks passed"
