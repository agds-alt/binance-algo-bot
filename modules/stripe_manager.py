"""
Stripe Payment Manager
Handles payment processing and license delivery
"""

import stripe
import os
from datetime import datetime, timedelta
from typing import Optional, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY', '')


class StripeManager:
    """
    Manage Stripe payments and license delivery

    Features:
    - Create checkout sessions
    - Handle webhooks
    - Auto-generate licenses
    - Subscription management
    """

    # Pricing tiers (in cents)
    PRICES = {
        'pro_monthly': {
            'amount': 4900,  # $49/month
            'currency': 'usd',
            'tier': 'pro',
            'duration_days': 30,
            'name': 'PRO Monthly'
        },
        'pro_yearly': {
            'amount': 39900,  # $399/year (save $189)
            'currency': 'usd',
            'tier': 'pro',
            'duration_days': 365,
            'name': 'PRO Yearly'
        },
        'premium_monthly': {
            'amount': 9900,  # $99/month
            'currency': 'usd',
            'tier': 'premium',
            'duration_days': 30,
            'name': 'Premium Monthly'
        },
        'premium_yearly': {
            'amount': 79900,  # $799/year (save $389)
            'currency': 'usd',
            'tier': 'premium',
            'duration_days': 365,
            'name': 'Premium Yearly'
        }
    }

    def __init__(self):
        """Initialize Stripe manager"""
        self.api_key = stripe.api_key

    def create_checkout_session(
        self,
        price_key: str,
        customer_email: str,
        success_url: str,
        cancel_url: str
    ) -> Optional[Dict]:
        """
        Create Stripe checkout session

        Args:
            price_key: Pricing tier key (e.g., 'pro_monthly')
            customer_email: Customer email
            success_url: Redirect URL on success
            cancel_url: Redirect URL on cancel

        Returns:
            Checkout session dict or None
        """
        try:
            if price_key not in self.PRICES:
                raise ValueError(f"Invalid price key: {price_key}")

            price_info = self.PRICES[price_key]

            # Create checkout session
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': price_info['currency'],
                        'unit_amount': price_info['amount'],
                        'product_data': {
                            'name': f"Binance Algo Bot - {price_info['name']}",
                            'description': f"{price_info['tier'].upper()} tier access for {price_info['duration_days']} days",
                        },
                    },
                    'quantity': 1,
                }],
                mode='payment',
                customer_email=customer_email,
                success_url=success_url + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=cancel_url,
                metadata={
                    'tier': price_info['tier'],
                    'duration_days': price_info['duration_days'],
                    'price_key': price_key
                }
            )

            return {
                'session_id': session.id,
                'url': session.url,
                'status': session.payment_status
            }

        except Exception as e:
            print(f"Error creating checkout session: {e}")
            return None

    def verify_payment(self, session_id: str) -> Optional[Dict]:
        """
        Verify payment was successful

        Args:
            session_id: Stripe checkout session ID

        Returns:
            Payment info dict or None
        """
        try:
            session = stripe.checkout.Session.retrieve(session_id)

            if session.payment_status == 'paid':
                return {
                    'customer_email': session.customer_details.email,
                    'amount_total': session.amount_total / 100,  # Convert to dollars
                    'currency': session.currency,
                    'tier': session.metadata.get('tier', 'pro'),
                    'duration_days': int(session.metadata.get('duration_days', 30)),
                    'payment_intent': session.payment_intent
                }

            return None

        except Exception as e:
            print(f"Error verifying payment: {e}")
            return None

    def generate_license_from_payment(
        self,
        session_id: str,
        license_manager
    ) -> Optional[Dict]:
        """
        Generate license after successful payment

        Args:
            session_id: Stripe checkout session ID
            license_manager: LicenseManager instance

        Returns:
            License info dict or None
        """
        try:
            # Verify payment
            payment_info = self.verify_payment(session_id)

            if not payment_info:
                return None

            # Generate license
            tier = payment_info['tier']
            duration_days = payment_info['duration_days']
            customer_email = payment_info['customer_email']

            license_key = license_manager.generate_license(
                tier=tier,
                duration_days=duration_days,
                max_activations=1
            )

            return {
                'license_key': license_key,
                'tier': tier,
                'duration_days': duration_days,
                'customer_email': customer_email,
                'amount_paid': payment_info['amount_total']
            }

        except Exception as e:
            print(f"Error generating license from payment: {e}")
            return None

    def handle_webhook(self, payload: bytes, sig_header: str) -> Optional[Dict]:
        """
        Handle Stripe webhook events

        Args:
            payload: Request payload
            sig_header: Stripe signature header

        Returns:
            Event data dict or None
        """
        try:
            webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET', '')

            if not webhook_secret:
                # For testing without webhook secret
                import json
                event = json.loads(payload)
            else:
                # Verify webhook signature
                event = stripe.Webhook.construct_event(
                    payload, sig_header, webhook_secret
                )

            # Handle different event types
            if event['type'] == 'checkout.session.completed':
                session = event['data']['object']

                return {
                    'type': 'payment_success',
                    'session_id': session['id'],
                    'customer_email': session['customer_details']['email'],
                    'tier': session['metadata'].get('tier', 'pro'),
                    'duration_days': int(session['metadata'].get('duration_days', 30))
                }

            elif event['type'] == 'payment_intent.succeeded':
                return {
                    'type': 'payment_confirmed',
                    'payment_intent': event['data']['object']['id']
                }

            return None

        except Exception as e:
            print(f"Webhook error: {e}")
            return None

    @staticmethod
    def format_price(amount_cents: int, currency: str = 'usd') -> str:
        """
        Format price for display

        Args:
            amount_cents: Amount in cents
            currency: Currency code

        Returns:
            Formatted price string
        """
        amount_dollars = amount_cents / 100

        if currency.lower() == 'usd':
            return f"${amount_dollars:,.2f}"
        else:
            return f"{amount_dollars:,.2f} {currency.upper()}"


def get_stripe_manager() -> StripeManager:
    """Get singleton Stripe manager instance"""
    return StripeManager()
