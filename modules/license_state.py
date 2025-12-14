"""
License State Manager
Manages local license state and validation
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple
from .license_manager import LicenseManager


class LicenseState:
    """
    Manages local license state

    Stores activated license information locally
    and handles validation on startup
    """

    def __init__(self, state_file: str = "data/license_state.json"):
        """
        Initialize License State Manager

        Args:
            state_file: Path to local state file
        """
        self.state_file = Path(state_file)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        self.license_manager = LicenseManager()
        self.state = self._load_state()

    def _load_state(self) -> dict:
        """Load state from file"""
        if not self.state_file.exists():
            return {
                'license_key': None,
                'tier': 'free',
                'hardware_id': None,
                'activated_at': None,
                'last_validated': None,
                'is_valid': False
            }

        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except:
            return {
                'license_key': None,
                'tier': 'free',
                'hardware_id': None,
                'activated_at': None,
                'last_validated': None,
                'is_valid': False
            }

    def _save_state(self):
        """Save state to file"""
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)

    def activate(self, license_key: str) -> Tuple[bool, str]:
        """
        Activate a license

        Args:
            license_key: License key to activate

        Returns:
            (success, message)
        """
        # Activate through license manager
        success, message, license = self.license_manager.activate_license(license_key)

        if not success:
            return False, message

        # Update local state
        self.state['license_key'] = license_key
        self.state['tier'] = license.tier
        self.state['hardware_id'] = license.hardware_id
        self.state['activated_at'] = datetime.utcnow().isoformat()
        self.state['last_validated'] = datetime.utcnow().isoformat()
        self.state['is_valid'] = True

        self._save_state()

        return True, f"License activated successfully! You now have {license.tier.upper()} tier access."

    def validate(self, force_check: bool = False) -> Tuple[bool, str, str]:
        """
        Validate current license

        Args:
            force_check: Force validation even if recently checked

        Returns:
            (is_valid, message, tier)
        """
        # No license activated
        if not self.state.get('license_key'):
            return False, "No license activated. Running in FREE tier mode.", 'free'

        # Check if validation is needed
        last_validated = self.state.get('last_validated')
        if not force_check and last_validated:
            try:
                last_check = datetime.fromisoformat(last_validated)
                hours_since_check = (datetime.utcnow() - last_check).seconds / 3600

                # Only validate every 24 hours
                if hours_since_check < 24:
                    if self.state.get('is_valid'):
                        return True, "License valid (cached)", self.state.get('tier', 'free')
            except:
                pass

        # Validate with license manager
        license_key = self.state['license_key']
        hardware_id = self.state.get('hardware_id')

        is_valid, message, tier = self.license_manager.validate_license(
            license_key,
            hardware_id
        )

        # Update state
        self.state['is_valid'] = is_valid
        self.state['tier'] = tier or 'free'
        self.state['last_validated'] = datetime.utcnow().isoformat()

        self._save_state()

        return is_valid, message, tier or 'free'

    def deactivate(self) -> Tuple[bool, str]:
        """
        Deactivate current license

        Returns:
            (success, message)
        """
        if not self.state.get('license_key'):
            return False, "No license is activated"

        # Reset state
        self.state = {
            'license_key': None,
            'tier': 'free',
            'hardware_id': None,
            'activated_at': None,
            'last_validated': None,
            'is_valid': False
        }

        self._save_state()

        return True, "License deactivated. Switched to FREE tier."

    def get_current_tier(self) -> str:
        """Get current tier"""
        # Validate first
        is_valid, _, tier = self.validate()

        if not is_valid:
            return 'free'

        return tier

    def get_license_info(self) -> Optional[dict]:
        """Get current license information"""
        if not self.state.get('license_key'):
            return None

        # Get info from license manager
        info = self.license_manager.get_license_info(self.state['license_key'])

        if info:
            info['locally_activated_at'] = self.state.get('activated_at')
            info['last_validated'] = self.state.get('last_validated')

        return info

    def is_trial(self) -> bool:
        """Check if current license is a trial"""
        info = self.get_license_info()
        if not info:
            return False

        return info.get('days_remaining', 0) <= 7  # Trial if < 7 days remaining

    def get_days_remaining(self) -> int:
        """Get days remaining on license"""
        info = self.get_license_info()
        if not info:
            return 0

        return info.get('days_remaining', 0)


# Singleton instance
_license_state_instance = None


def get_license_state() -> LicenseState:
    """Get singleton license state instance"""
    global _license_state_instance
    if _license_state_instance is None:
        _license_state_instance = LicenseState()
    return _license_state_instance


# Example usage
if __name__ == "__main__":
    state = get_license_state()

    print("Current License State:")
    print(f"  Tier: {state.get_current_tier()}")
    print(f"  Valid: {state.state.get('is_valid')}")

    info = state.get_license_info()
    if info:
        print(f"\nLicense Info:")
        for key, value in info.items():
            print(f"  {key}: {value}")
    else:
        print("\n  No license activated (FREE tier)")
