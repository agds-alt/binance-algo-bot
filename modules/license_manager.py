"""
License Management System
Handles license key generation, validation, activation, and expiry
"""

import hashlib
import secrets
import hmac
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict
from dataclasses import dataclass, asdict
from pathlib import Path
import uuid

@dataclass
class License:
    """License data structure"""
    license_key: str
    tier: str  # 'free', 'pro', 'premium', 'enterprise'
    user_id: str
    email: str
    issued_date: datetime
    expiry_date: datetime
    hardware_id: Optional[str] = None
    is_active: bool = True
    max_activations: int = 1
    activation_count: int = 0
    metadata: Dict = None

    def to_dict(self):
        """Convert to dictionary for storage"""
        data = asdict(self)
        data['issued_date'] = self.issued_date.isoformat()
        data['expiry_date'] = self.expiry_date.isoformat()
        data['metadata'] = json.dumps(self.metadata or {})
        return data

    @staticmethod
    def from_dict(data: dict):
        """Create License from dictionary"""
        data['issued_date'] = datetime.fromisoformat(data['issued_date'])
        data['expiry_date'] = datetime.fromisoformat(data['expiry_date'])
        data['metadata'] = json.loads(data.get('metadata', '{}'))
        return License(**data)


class LicenseManager:
    """
    License Management System

    Features:
    - Generate license keys
    - Validate licenses
    - Hardware binding
    - Expiry management
    - Activation limits
    """

    def __init__(self, db_path: str = "data/licenses.db", secret_key: str = None):
        """
        Initialize License Manager

        Args:
            db_path: Path to SQLite database
            secret_key: Secret key for HMAC signing (keep this safe!)
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Secret key for signing - CHANGE THIS IN PRODUCTION
        self.secret_key = secret_key or "CHANGE_THIS_SECRET_KEY_IN_PRODUCTION"

        self._init_database()

    def _init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS licenses (
                license_key TEXT PRIMARY KEY,
                tier TEXT NOT NULL,
                user_id TEXT NOT NULL,
                email TEXT NOT NULL,
                issued_date TEXT NOT NULL,
                expiry_date TEXT NOT NULL,
                hardware_id TEXT,
                is_active INTEGER DEFAULT 1,
                max_activations INTEGER DEFAULT 1,
                activation_count INTEGER DEFAULT 0,
                metadata TEXT DEFAULT '{}'
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                license_key TEXT NOT NULL,
                hardware_id TEXT NOT NULL,
                activated_at TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                ip_address TEXT,
                FOREIGN KEY (license_key) REFERENCES licenses(license_key)
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_license_user
            ON licenses(user_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_license_email
            ON licenses(email)
        """)

        conn.commit()
        conn.close()

    def generate_license_key(self, tier: str, prefix: str = None) -> str:
        """
        Generate a unique license key

        Format: PREFIX-XXXX-XXXX-XXXX-XXXX

        Args:
            tier: License tier (free/pro/premium/enterprise)
            prefix: Optional prefix (default: tier-based)

        Returns:
            Formatted license key
        """
        # Tier-based prefix
        tier_prefixes = {
            'free': 'FREE',
            'pro': 'PRO',
            'premium': 'PREM',
            'enterprise': 'ENT'
        }

        prefix = prefix or tier_prefixes.get(tier.lower(), 'BOT')

        # Generate random segments
        segments = []
        for _ in range(4):
            segment = secrets.token_hex(2).upper()  # 4 chars
            segments.append(segment)

        license_key = f"{prefix}-{'-'.join(segments)}"

        # Add checksum for validation
        checksum = self._calculate_checksum(license_key)

        return f"{license_key}-{checksum}"

    def _calculate_checksum(self, license_key: str) -> str:
        """Calculate HMAC checksum for license key"""
        signature = hmac.new(
            self.secret_key.encode(),
            license_key.encode(),
            hashlib.sha256
        ).hexdigest()[:4].upper()
        return signature

    def validate_checksum(self, license_key: str) -> bool:
        """Validate license key checksum"""
        if '-' not in license_key:
            return False

        parts = license_key.split('-')
        if len(parts) < 2:
            return False

        checksum = parts[-1]
        key_without_checksum = '-'.join(parts[:-1])

        expected_checksum = self._calculate_checksum(key_without_checksum)

        return hmac.compare_digest(checksum, expected_checksum)

    def create_license(
        self,
        tier: str,
        email: str,
        duration_days: int = 30,
        user_id: str = None,
        max_activations: int = 1,
        metadata: dict = None
    ) -> License:
        """
        Create a new license

        Args:
            tier: License tier
            email: User email
            duration_days: License duration in days
            user_id: Optional user ID (generated if not provided)
            max_activations: Maximum number of devices
            metadata: Additional metadata

        Returns:
            License object
        """
        user_id = user_id or str(uuid.uuid4())
        license_key = self.generate_license_key(tier)

        issued_date = datetime.utcnow()

        # Tier-based durations
        tier_durations = {
            'free': 365,  # Free tier - 1 year (renewable)
            'pro': duration_days,
            'premium': duration_days,
            'enterprise': duration_days
        }

        expiry_date = issued_date + timedelta(days=tier_durations.get(tier.lower(), duration_days))

        license = License(
            license_key=license_key,
            tier=tier.lower(),
            user_id=user_id,
            email=email,
            issued_date=issued_date,
            expiry_date=expiry_date,
            is_active=True,
            max_activations=max_activations,
            activation_count=0,
            metadata=metadata or {}
        )

        # Save to database
        self._save_license(license)

        return license

    def _save_license(self, license: License):
        """Save license to database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        data = license.to_dict()

        cursor.execute("""
            INSERT OR REPLACE INTO licenses
            (license_key, tier, user_id, email, issued_date, expiry_date,
             hardware_id, is_active, max_activations, activation_count, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['license_key'],
            data['tier'],
            data['user_id'],
            data['email'],
            data['issued_date'],
            data['expiry_date'],
            data['hardware_id'],
            1 if data['is_active'] else 0,
            data['max_activations'],
            data['activation_count'],
            data['metadata']
        ))

        conn.commit()
        conn.close()

    def get_license(self, license_key: str) -> Optional[License]:
        """Retrieve license from database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM licenses WHERE license_key = ?
        """, (license_key,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        columns = [
            'license_key', 'tier', 'user_id', 'email', 'issued_date',
            'expiry_date', 'hardware_id', 'is_active', 'max_activations',
            'activation_count', 'metadata'
        ]

        data = dict(zip(columns, row))
        data['is_active'] = bool(data['is_active'])

        return License.from_dict(data)

    def activate_license(
        self,
        license_key: str,
        hardware_id: str = None,
        ip_address: str = None
    ) -> Tuple[bool, str, Optional[License]]:
        """
        Activate a license on a specific hardware

        Args:
            license_key: License key
            hardware_id: Hardware identifier (generated if not provided)
            ip_address: IP address of activation

        Returns:
            (success, message, license)
        """
        # Validate checksum
        if not self.validate_checksum(license_key):
            return False, "Invalid license key format", None

        # Get license
        license = self.get_license(license_key)
        if not license:
            return False, "License key not found", None

        # Check if active
        if not license.is_active:
            return False, "License is deactivated", None

        # Check expiry
        if datetime.utcnow() > license.expiry_date:
            return False, "License has expired", None

        # Generate hardware ID if not provided
        if not hardware_id:
            hardware_id = self._generate_hardware_id()

        # Check if already activated on this hardware
        if license.hardware_id == hardware_id:
            self._update_last_seen(license_key, hardware_id)
            return True, "License already activated on this device", license

        # Check activation limit
        if license.activation_count >= license.max_activations:
            return False, f"Maximum activations ({license.max_activations}) reached", None

        # Activate
        license.hardware_id = hardware_id
        license.activation_count += 1

        self._save_license(license)
        self._record_activation(license_key, hardware_id, ip_address)

        return True, "License activated successfully", license

    def _generate_hardware_id(self) -> str:
        """
        Generate hardware ID based on system characteristics

        Uses: MAC address, hostname, UUID
        """
        import platform
        import socket

        try:
            # Get MAC address
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                           for elements in range(0, 2*6, 2)][::-1])

            # Get hostname
            hostname = socket.gethostname()

            # Combine and hash
            combined = f"{mac}-{hostname}-{platform.machine()}"
            hardware_id = hashlib.sha256(combined.encode()).hexdigest()[:16].upper()

            return hardware_id
        except:
            # Fallback to random UUID
            return str(uuid.uuid4()).replace('-', '')[:16].upper()

    def _record_activation(self, license_key: str, hardware_id: str, ip_address: str = None):
        """Record activation in database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        now = datetime.utcnow().isoformat()

        cursor.execute("""
            INSERT INTO activations
            (license_key, hardware_id, activated_at, last_seen, ip_address)
            VALUES (?, ?, ?, ?, ?)
        """, (license_key, hardware_id, now, now, ip_address))

        conn.commit()
        conn.close()

    def _update_last_seen(self, license_key: str, hardware_id: str):
        """Update last seen timestamp"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        now = datetime.utcnow().isoformat()

        cursor.execute("""
            UPDATE activations
            SET last_seen = ?
            WHERE license_key = ? AND hardware_id = ?
        """, (now, license_key, hardware_id))

        conn.commit()
        conn.close()

    def validate_license(
        self,
        license_key: str,
        hardware_id: str = None
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Validate a license

        Returns:
            (is_valid, message, tier)
        """
        # Validate checksum
        if not self.validate_checksum(license_key):
            return False, "Invalid license key format", None

        # Get license
        license = self.get_license(license_key)
        if not license:
            return False, "License key not found", None

        # Check if active
        if not license.is_active:
            return False, "License is deactivated", None

        # Check expiry
        if datetime.utcnow() > license.expiry_date:
            return False, "License has expired", None

        # Check hardware binding
        if hardware_id:
            if not license.hardware_id:
                return False, "License not activated on any device", None

            if license.hardware_id != hardware_id:
                return False, "License activated on different device", None

        return True, "License is valid", license.tier

    def deactivate_license(self, license_key: str) -> Tuple[bool, str]:
        """Deactivate a license"""
        license = self.get_license(license_key)
        if not license:
            return False, "License not found"

        license.is_active = False
        self._save_license(license)

        return True, "License deactivated"

    def extend_license(self, license_key: str, days: int) -> Tuple[bool, str]:
        """Extend license expiry"""
        license = self.get_license(license_key)
        if not license:
            return False, "License not found"

        license.expiry_date += timedelta(days=days)
        self._save_license(license)

        return True, f"License extended by {days} days"

    def upgrade_license(self, license_key: str, new_tier: str) -> Tuple[bool, str]:
        """Upgrade license tier"""
        license = self.get_license(license_key)
        if not license:
            return False, "License not found"

        tier_hierarchy = ['free', 'pro', 'premium', 'enterprise']

        if tier_hierarchy.index(new_tier.lower()) <= tier_hierarchy.index(license.tier):
            return False, "Cannot downgrade or maintain same tier"

        license.tier = new_tier.lower()
        self._save_license(license)

        return True, f"License upgraded to {new_tier}"

    def get_license_info(self, license_key: str) -> Optional[dict]:
        """Get license information"""
        license = self.get_license(license_key)
        if not license:
            return None

        days_remaining = (license.expiry_date - datetime.utcnow()).days

        return {
            'license_key': license.license_key,
            'tier': license.tier.upper(),
            'email': license.email,
            'is_active': license.is_active,
            'issued_date': license.issued_date.strftime('%Y-%m-%d'),
            'expiry_date': license.expiry_date.strftime('%Y-%m-%d'),
            'days_remaining': max(0, days_remaining),
            'is_expired': datetime.utcnow() > license.expiry_date,
            'activation_count': license.activation_count,
            'max_activations': license.max_activations,
            'hardware_id': license.hardware_id[:8] + '...' if license.hardware_id else None,
        }


# Example usage
if __name__ == "__main__":
    # Initialize manager
    manager = LicenseManager()

    # Create a PRO license
    license = manager.create_license(
        tier='pro',
        email='user@example.com',
        duration_days=30,
        metadata={'source': 'stripe', 'plan': 'monthly'}
    )

    print(f"Generated License: {license.license_key}")
    print(f"Tier: {license.tier}")
    print(f"Expires: {license.expiry_date.strftime('%Y-%m-%d')}")

    # Activate license
    success, message, activated_license = manager.activate_license(
        license.license_key,
        ip_address='192.168.1.1'
    )

    print(f"\nActivation: {message}")

    # Validate license
    is_valid, validation_msg, tier = manager.validate_license(license.license_key)
    print(f"Validation: {validation_msg} (Tier: {tier})")

    # Get license info
    info = manager.get_license_info(license.license_key)
    print(f"\nLicense Info:")
    for key, value in info.items():
        print(f"  {key}: {value}")
