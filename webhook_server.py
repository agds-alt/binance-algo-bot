"""
Stripe Webhook Server
Handles Stripe payment events and auto-generates licenses

Run with:
    python webhook_server.py

Then expose with ngrok for testing:
    ngrok http 5000

Add the ngrok URL to Stripe Dashboard webhooks
"""

from flask import Flask, request, jsonify
import stripe
import os
from dotenv import load_dotenv
from modules.stripe_manager import get_stripe_manager
from modules.license_manager import LicenseManager

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY', '')
webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET', '')

stripe_manager = get_stripe_manager()
license_manager = LicenseManager()


@app.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    """
    Handle Stripe webhook events

    Events handled:
    - checkout.session.completed: Payment successful
    - payment_intent.succeeded: Payment confirmed
    """
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')

    try:
        # Verify webhook signature
        if webhook_secret:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        else:
            # For testing without signature verification
            import json
            event = json.loads(payload)

        # Handle different event types
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']

            print(f"\n🎉 Payment successful!")
            print(f"Session ID: {session['id']}")
            print(f"Customer Email: {session['customer_details']['email']}")
            print(f"Amount: ${session['amount_total'] / 100}")

            # Generate license
            tier = session['metadata'].get('tier', 'pro')
            duration_days = int(session['metadata'].get('duration_days', 30))
            customer_email = session['customer_details']['email']

            license_key = license_manager.generate_license(
                tier=tier,
                duration_days=duration_days,
                max_activations=1
            )

            print(f"✅ License generated: {license_key}")
            print(f"Tier: {tier}")
            print(f"Duration: {duration_days} days")

            # TODO: Send email to customer with license key
            # For now, just log it
            print(f"\n📧 Email would be sent to: {customer_email}")
            print(f"License Key: {license_key}\n")

            return jsonify({
                'status': 'success',
                'license_key': license_key,
                'tier': tier
            }), 200

        elif event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            print(f"💰 Payment confirmed: {payment_intent['id']}")

            return jsonify({'status': 'success'}), 200

        else:
            print(f"Unhandled event type: {event['type']}")
            return jsonify({'status': 'ignored'}), 200

    except ValueError as e:
        # Invalid payload
        print(f"❌ Invalid payload: {e}")
        return jsonify({'error': 'Invalid payload'}), 400

    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        print(f"❌ Invalid signature: {e}")
        return jsonify({'error': 'Invalid signature'}), 400

    except Exception as e:
        # Other errors
        print(f"❌ Webhook error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'service': 'Stripe Webhook Server',
        'stripe_configured': bool(stripe.api_key)
    }), 200


if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("🚀 STRIPE WEBHOOK SERVER")
    print("=" * 70)
    print(f"Stripe API Key: {'✅ Configured' if stripe.api_key else '❌ Not configured'}")
    print(f"Webhook Secret: {'✅ Configured' if webhook_secret else '⚠️  Not configured (signatures disabled)'}")
    print("\nServer starting on http://localhost:5000")
    print("Webhook endpoint: http://localhost:5000/webhook/stripe")
    print("\nFor testing, expose with ngrok:")
    print("  ngrok http 5000")
    print("Then add the ngrok URL to Stripe Dashboard webhooks")
    print("=" * 70 + "\n")

    # Add Flask to requirements if not present
    try:
        import flask
    except ImportError:
        print("⚠️  Flask not installed. Installing...")
        import subprocess
        subprocess.run(['pip', 'install', 'flask==3.0.0'])

    app.run(debug=True, port=5000, host='0.0.0.0')
