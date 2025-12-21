"""
Pricing & Checkout Page
Stripe payment integration for license purchase
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.stripe_manager import get_stripe_manager, StripeManager
from modules.license_manager import LicenseManager

st.set_page_config(page_title="Pricing", page_icon="💳", layout="wide")

# Enhanced CSS
st.markdown("""
<style>
    .pricing-card {
        background: white;
        border: 2px solid #e5e7eb;
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem 0;
        transition: all 0.3s;
    }
    .pricing-card:hover {
        border-color: #3b82f6;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        transform: translateY(-5px);
    }
    .pricing-card.featured {
        border-color: #3b82f6;
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        position: relative;
    }
    .price {
        font-size: 3rem;
        font-weight: 800;
        color: #1f2937;
        margin: 1rem 0;
    }
    .price-period {
        font-size: 1rem;
        color: #6b7280;
    }
    .feature-list {
        list-style: none;
        padding: 0;
        margin: 1.5rem 0;
    }
    .feature-item {
        padding: 0.5rem 0;
        color: #374151;
    }
    .featured-badge {
        position: absolute;
        top: -12px;
        right: 20px;
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        color: white;
        padding: 0.5rem 1.5rem;
        border-radius: 25px;
        font-weight: 700;
        font-size: 0.85rem;
    }
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        text-align: center;
        color: #6b7280;
        font-size: 1.2rem;
        margin-bottom: 3rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">💳 Pricing & Plans</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Choose the perfect plan for your trading needs</div>', unsafe_allow_html=True)

# Initialize Stripe manager
stripe_manager = get_stripe_manager()

# Check if user is already PRO/Premium
if 'tier' not in st.session_state:
    st.session_state.tier = 'free'

current_tier = st.session_state.get('tier', 'free')

if current_tier in ['pro', 'premium']:
    st.success(f"✅ You're currently on the **{current_tier.upper()}** plan!")
    st.info("Your subscription is active. You have full access to all features.")
    st.markdown("---")

# Show success message if coming from payment
if 'success' in st.query_params:
    session_id = st.query_params.get('session_id', [''])[0] if 'session_id' in st.query_params else None

    if session_id:
        st.balloons()
        st.success("🎉 **Payment Successful!**")

        # Verify payment and generate license
        license_manager = LicenseManager()
        license_info = stripe_manager.generate_license_from_payment(session_id, license_manager)

        if license_info:
            st.markdown(f"""
            ### Your License Key:
            ```
            {license_info['license_key']}
            ```

            **Tier:** {license_info['tier'].upper()}
            **Duration:** {license_info['duration_days']} days
            **Amount Paid:** ${license_info['amount_paid']}

            Please save this license key. You can activate it in the **License** page.
            """)

            if st.button("Go to License Page", type="primary"):
                st.switch_page("pages/5_License.py")
        else:
            st.error("Unable to generate license. Please contact support with your payment confirmation.")

# Pricing tiers
st.markdown("---")
st.markdown("## Choose Your Plan")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="pricing-card">
        <h2 style="color: #3b82f6; font-weight: 700;">PRO Plan</h2>
        <div class="price">$49<span class="price-period">/month</span></div>
        <div style="color: #6b7280; margin-bottom: 1rem;">or $399/year (save $189)</div>

        <div class="feature-list">
            <div class="feature-item">✅ Live Trading 24/7</div>
            <div class="feature-item">✅ Multi-pair trading (5 pairs)</div>
            <div class="feature-item">✅ Advanced strategies</div>
            <div class="feature-item">✅ Risk management</div>
            <div class="feature-item">✅ Telegram notifications</div>
            <div class="feature-item">✅ Performance analytics</div>
            <div class="feature-item">✅ Backtesting engine</div>
            <div class="feature-item">✅ Trade history export</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    pricing_col1, pricing_col2 = st.columns(2)

    with pricing_col1:
        if st.button("💳 Buy Monthly ($49)", use_container_width=True, type="primary", disabled=current_tier == 'pro'):
            with st.spinner("Creating checkout session..."):
                customer_email = st.text_input("Email", key="email_pro_monthly")

                if customer_email:
                    success_url = "http://localhost:8501/Pricing?success=true"
                    cancel_url = "http://localhost:8501/Pricing"

                    session = stripe_manager.create_checkout_session(
                        price_key='pro_monthly',
                        customer_email=customer_email,
                        success_url=success_url,
                        cancel_url=cancel_url
                    )

                    if session:
                        st.markdown(f"[Click here to complete payment]({session['url']})")
                        st.info("You will be redirected to Stripe checkout...")
                    else:
                        st.error("Unable to create checkout session. Please check your Stripe configuration.")

    with pricing_col2:
        if st.button("💳 Buy Yearly ($399)", use_container_width=True, disabled=current_tier == 'pro'):
            with st.spinner("Creating checkout session..."):
                customer_email = st.text_input("Email", key="email_pro_yearly")

                if customer_email:
                    success_url = "http://localhost:8501/Pricing?success=true"
                    cancel_url = "http://localhost:8501/Pricing"

                    session = stripe_manager.create_checkout_session(
                        price_key='pro_yearly',
                        customer_email=customer_email,
                        success_url=success_url,
                        cancel_url=cancel_url
                    )

                    if session:
                        st.markdown(f"[Click here to complete payment]({session['url']})")
                        st.info("You will be redirected to Stripe checkout...")
                    else:
                        st.error("Unable to create checkout session. Please check your Stripe configuration.")

with col2:
    st.markdown("""
    <div class="pricing-card featured">
        <div class="featured-badge">⭐ BEST VALUE</div>
        <h2 style="color: #8b5cf6; font-weight: 700;">Premium Plan</h2>
        <div class="price">$99<span class="price-period">/month</span></div>
        <div style="color: #6b7280; margin-bottom: 1rem;">or $799/year (save $389)</div>

        <div class="feature-list">
            <div class="feature-item">✅ <strong>Everything in PRO</strong></div>
            <div class="feature-item">✅ Unlimited pairs</div>
            <div class="feature-item">✅ Advanced AI strategies</div>
            <div class="feature-item">✅ Custom indicators</div>
            <div class="feature-item">✅ Priority support</div>
            <div class="feature-item">✅ Monthly performance reports</div>
            <div class="feature-item">✅ API access</div>
            <div class="feature-item">✅ White-label option</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    pricing_col1, pricing_col2 = st.columns(2)

    with pricing_col1:
        if st.button("💳 Buy Monthly ($99)", use_container_width=True, type="primary", disabled=current_tier == 'premium'):
            with st.spinner("Creating checkout session..."):
                customer_email = st.text_input("Email", key="email_premium_monthly")

                if customer_email:
                    success_url = "http://localhost:8501/Pricing?success=true"
                    cancel_url = "http://localhost:8501/Pricing"

                    session = stripe_manager.create_checkout_session(
                        price_key='premium_monthly',
                        customer_email=customer_email,
                        success_url=success_url,
                        cancel_url=cancel_url
                    )

                    if session:
                        st.markdown(f"[Click here to complete payment]({session['url']})")
                        st.info("You will be redirected to Stripe checkout...")
                    else:
                        st.error("Unable to create checkout session. Please check your Stripe configuration.")

    with pricing_col2:
        if st.button("💳 Buy Yearly ($799)", use_container_width=True, disabled=current_tier == 'premium'):
            with st.spinner("Creating checkout session..."):
                customer_email = st.text_input("Email", key="email_premium_yearly")

                if customer_email:
                    success_url = "http://localhost:8501/Pricing?success=true"
                    cancel_url = "http://localhost:8501/Pricing"

                    session = stripe_manager.create_checkout_session(
                        price_key='premium_yearly',
                        customer_email=customer_email,
                        success_url=success_url,
                        cancel_url=cancel_url
                    )

                    if session:
                        st.markdown(f"[Click here to complete payment]({session['url']})")
                        st.info("You will be redirected to Stripe checkout...")
                    else:
                        st.error("Unable to create checkout session. Please check your Stripe configuration.")

# FAQ Section
st.markdown("---")
st.markdown("## Frequently Asked Questions")

with st.expander("🔒 Is my payment secure?"):
    st.markdown("""
    Yes! All payments are processed securely through Stripe, a PCI-compliant payment processor.
    We never see or store your credit card information.
    """)

with st.expander("💳 What payment methods are accepted?"):
    st.markdown("""
    We accept all major credit cards (Visa, Mastercard, American Express) and debit cards through Stripe.
    """)

with st.expander("🔄 Can I cancel anytime?"):
    st.markdown("""
    Yes! Monthly plans can be canceled anytime. Yearly plans are non-refundable but you'll have access
    for the full year you paid for.
    """)

with st.expander("📧 Will I receive my license immediately?"):
    st.markdown("""
    Yes! After successful payment, your license key will be displayed on screen and sent to your email.
    You can activate it immediately in the License page.
    """)

with st.expander("💬 What if I need help?"):
    st.markdown("""
    PRO and Premium users get priority support via email and Telegram.
    Contact us at support@binancealgobot.com
    """)
