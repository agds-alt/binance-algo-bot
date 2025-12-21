"""
Quick test script for Telegram notifications
"""

import asyncio
from modules.telegram_bot import TelegramNotifier

async def test_telegram():
    """Test Telegram notifications"""

    notifier = TelegramNotifier()

    if not notifier.enabled:
        print("❌ Telegram not configured!")
        print("Please set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env file")
        return False

    print("✅ Telegram is configured")
    print(f"Bot Token: {notifier.bot_token[:10]}...")
    print(f"Chat ID: {notifier.chat_id}")
    print()

    try:
        # Test 1: Simple message
        print("📤 Sending test message...")
        await notifier.send_message("🤖 Test from Binance Algo Bot!")
        print("✅ Test message sent!")
        print()

        # Test 2: Trade entry notification
        print("📤 Sending trade entry notification...")
        await notifier.notify_trade_entry({
            'symbol': 'BNBUSDT',
            'side': 'LONG',
            'entry_price': 245.30,
            'quantity': 10.5,
            'stop_loss': 242.00,
            'take_profit_1': 250.00,
            'leverage': 5,
            'risk_usd': 50.00
        })
        print("✅ Trade entry notification sent!")
        print()

        # Test 3: Take profit notification
        print("📤 Sending take profit notification...")
        await notifier.notify_take_profit({
            'symbol': 'BNBUSDT',
            'tp_level': 1,
            'price': 250.00,
            'quantity_closed': 5.25,
            'profit': 45.30,
            'percentage': 1.84
        })
        print("✅ Take profit notification sent!")
        print()

        # Test 4: Daily summary
        print("📤 Sending daily summary...")
        await notifier.send_daily_summary({
            'total_trades': 12,
            'wins': 8,
            'losses': 4,
            'pnl': 234.56,
            'win_rate': 66.67,
            'balance': 10234.56
        })
        print("✅ Daily summary sent!")
        print()

        print("=" * 50)
        print("✅ ALL TESTS PASSED!")
        print("Check your Telegram to see the notifications")
        print("=" * 50)

        return True

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_telegram())

    if not success:
        print("\n💡 To configure Telegram:")
        print("1. Get Bot Token from @BotFather on Telegram")
        print("2. Get Chat ID from @userinfobot on Telegram")
        print("3. Add to .env file:")
        print("   TELEGRAM_BOT_TOKEN=your_token_here")
        print("   TELEGRAM_CHAT_ID=your_chat_id_here")
        print("\nOr configure via dashboard at http://localhost:8501")
