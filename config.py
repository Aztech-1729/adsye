# ==================================================================
# This code is licensed under @Axcne
# Built by Axcne - All rights reserved
# Unauthorized copying, modification, or distribution is prohibited
# Contact: @Axcne on Telegram for licensing inquiries
# ==================================================================

import os

BOT_CONFIG = {
    'api_id': int(os.getenv('TELEGRAM_API_ID', '23131964')),
    'api_hash': os.getenv('TELEGRAM_API_HASH', '1f383b963dd342881edce03bd1e686a5'),
    'bot_token': os.getenv('BOT_TOKEN', '8586436271:AAHR109uVFouFkyukxIoR_DQDp6RhDwtFpk'),
    'owner_id': int(os.getenv('OWNER_ID', '6670166083')),
    'access_password': os.getenv('ACCESS_PASSWORD', 'ADSREACHOP'),
    'mongo_uri': os.getenv('MONGO_URI', 'mongodb+srv://dbotp60_db_user:ARSHTYAGI@cluster0.4b8xz3a.mongodb.net/?appName=Cluster0'),
    'db_name': os.getenv('MONGO_DB_NAME', 'testdb'),
    'logger_bot_token': os.getenv('LOGGER_BOT_TOKEN', '8301517923:AAEYFRMTnR9ZTN-X11LIbF4mcUBYMunOCtA'),
    'logger_bot_username': os.getenv('LOGGER_BOT_USERNAME', 'AdsyeLogsBot'),
}

# ===================== PLAN TIERS =====================
# Scout (Free), Grow (₹69), Prime (₹199), Dominion (₹389)

PLAN_SCOUT = {
    'name': 'Scout',
    'price': 0,
    'price_display': 'Free',
    'tagline': 'Perfect for beginners exploring automation',
    'emoji': '🔰',
    'max_accounts': 1,
    'group_delay': 180,
    'msg_delay': 60,
    'round_delay': 10800,
    'auto_reply_enabled': False,
    'max_topics': 2,
    'max_groups_per_topic': 10,
    'logs_enabled': False,
    'description': '1 account, slow delays, basic features',
}

PLAN_GROW = {
    'name': 'Grow',
    'price': 69,
    'price_display': '₹69',
    'tagline': 'Scale your reach with multiple accounts',
    'emoji': '📈',
    'max_accounts': 3,
    'group_delay': 120,
    'msg_delay': 45,
    'round_delay': 7200,
    'auto_reply_enabled': True,
    'max_topics': 5,
    'max_groups_per_topic': 50,
    'logs_enabled': True,
    'description': '3 accounts, medium delays, auto-reply + logs',
}

PLAN_PRIME = {
    'name': 'Prime',
    'price': 199,
    'price_display': '₹199',
    'tagline': 'Advanced automation for serious marketers',
    'emoji': '⭐',
    'max_accounts': 7,
    'group_delay': 80,
    'msg_delay': 30,
    'round_delay': 5400,
    'auto_reply_enabled': True,
    'max_topics': 9,
    'max_groups_per_topic': 100,
    'logs_enabled': True,
    'description': '7 accounts, faster delays, full features',
}

PLAN_DOMINION = {
    'name': 'Dominion',
    'price': 389,
    'price_display': '₹389',
    'tagline': 'Ultimate power for advertising domination',
    'emoji': '👑',
    'max_accounts': 15,
    'group_delay': 60,
    'msg_delay': 20,
    'round_delay': 3600,
    'auto_reply_enabled': True,
    'max_topics': 15,
    'max_groups_per_topic': 200,
    'logs_enabled': True,
    'description': '15 accounts, fastest delays, priority support',
}

# Admin-only plan for quick UPI verification testing
PLAN_TEST = {
    'name': 'Test',
    'price': 1,
    'price_display': '₹1',
    'tagline': 'Admin test payment (₹1)',
    'emoji': '🧪',
    'max_accounts': 2,
    'group_delay': 180,
    'msg_delay': 60,
    'round_delay': 10800,
    'auto_reply_enabled': False,
    'max_topics': 1,
    'max_groups_per_topic': 10,
    'logs_enabled': False,
    'description': 'Admin-only test plan (₹1) to validate payment flow',
}

PLANS = {
    'scout': PLAN_SCOUT,
    'grow': PLAN_GROW,
    'prime': PLAN_PRIME,
    'dominion': PLAN_DOMINION,
    'test': PLAN_TEST,
}

# Backwards compat (old code references FREE_TIER/PREMIUM_TIER)
FREE_TIER = PLAN_SCOUT.copy()
PREMIUM_TIER = PLAN_DOMINION.copy()
ADMIN_USERNAME = "axcne"

MESSAGES = {
    'welcome': "Welcome to Ads Bot!\n\nManage your Telegram advertising campaigns with ease.",
    'welcome_image': os.getenv('WELCOME_IMAGE', 'https://i.ibb.co/k2Jrvth9/x.jpg'),

    # ===================== Account Profile Templates =====================
    # Applied to ALL added accounts when user opens dashboard (/start).
    # First name is preserved as-is.
    # Last name is forced to this tag (removes any existing last name).
    'account_last_name_tag': '| @GoAdsye',
    # Bio is forced to this text (removes any existing bio).
    'account_bio': 'Smart Ads Automation • @AdsyeBot',
    'support_link': os.getenv('SUPPORT_LINK', 'https://t.me/AdsReachSupport'),
    'updates_link': os.getenv('UPDATES_LINK', 'https://t.me/AdsReachUpdates'),
    'premium_contact': "Contact admin to purchase Premium access.\n\nPremium Benefits:\n- More accounts\n- Faster delays\n- Auto-reply feature\n- Detailed logs\n- Priority support",
    
    # Privacy Policy
    'privacy_short': (
        "<b>📜 Privacy Policy & Terms of Service</b>\n\n"
        "<blockquote>By using Adsye Bot, you acknowledge and agree to:\n\n"
        "<b>✓ Service Usage:</b>\n"
        "• Automated broadcasting across Telegram groups\n"
        "• Responsible and ethical use of the platform\n"
        "• Compliance with Telegram's Terms of Service\n\n"
        "<b>✓ Data & Privacy:</b>\n"
        "• Session data stored securely (encrypted)\n"
        "• Account credentials never shared\n"
        "• Analytics for service improvement only\n"
        "• No data sold to third parties\n\n"
        "<b>✓ Your Responsibility:</b>\n"
        "• Avoid spam or abusive content\n"
        "• Respect group rules and user privacy\n"
        "• Use reasonable delays between messages</blockquote>\n\n"
        "<i>We prioritize your security and privacy.</i>"
    ),
    'privacy_full_link': os.getenv('PRIVACY_URL', 'https://jarvisads.site/privacy'),
}

# ===================== Force Join (Config-based) =====================
# If enabled, users must join BOTH a channel and a group before using the bot.
# Use usernames (without @) so buttons can point to public links.
FORCE_JOIN = {
    'enabled': os.getenv('FORCE_JOIN_ENABLED', 'true').lower() in ('1', 'true', 'yes', 'on'),

    # Public @usernames (without @). Example: 'AdsReachUpdates'
    'channel_username': os.getenv('FORCE_JOIN_CHANNEL', 'GoAdsye'),
    'group_username': os.getenv('FORCE_JOIN_GROUP', 'JarvisGc'),

    # Lock screen visuals
    'image_url': os.getenv('FORCE_JOIN_IMAGE', 'https://i.ibb.co/k2Jrvth9/x.jpg'),
    'message': os.getenv(
        'FORCE_JOIN_MESSAGE',
        "**Access Locked**\n\nPlease join our **Channel** and **Group** to use this bot.\n\nAfter joining, click **Verify**."
    ),
}

# Plan selection screen image
PLAN_IMAGE_URL = os.getenv('PLAN_IMAGE_URL', 'https://i.ibb.co/k2Jrvth9/x.jpg')

# ===================== Payment Gateway Config =====================
# Oxapay crypto payment gateway
OXAPAY_CONFIG = {
    'merchant_api_key': os.getenv('OXAPAY_MERCHANT_KEY', ''),  # Your Oxapay merchant key (only one needed!)
    'api_url': 'https://api.oxapay.com/merchants/request',
    'webhook_url': os.getenv('OXAPAY_WEBHOOK_URL', 'https://webhook-adsye.onrender.com/oxapay/webhook'),  
    'webhook_secret': os.getenv('WEBHOOK_SECRET', 'isKQlLSdYlJ0bcorMf_LQfWOJJM9Kr_q8AV79qY8M24'),  
    'currencies': ['USDT', 'BTC', 'ETH', 'LTC', 'TRX'],  
}

ADMIN_SETTINGS = {
    'default_premium_accounts': 5,
    'default_premium_days': 30,
}

INTERVAL_PRESETS = {
    'slow': {'group_delay': 180, 'msg_delay': 60, 'round_delay': 10800, 'name': 'Slow (Safe)'},
    'medium': {'group_delay': 120, 'msg_delay': 45, 'round_delay': 7200, 'name': 'Medium (Balanced)'},
    'fast': {'group_delay': 60, 'msg_delay': 20, 'round_delay': 3600, 'name': 'Fast (Risky)'},
}

TOPICS = ['instagram', 'exchange', 'twitter', 'telegram', 'minecraft', 'tiktok', 'youtube', 'whatsapp', 'other']

# Proxy configuration for account logins
# Format: list of proxy dicts with type, host, port, username (optional), password (optional)
# Types: 'socks5', 'socks4', 'http'
# Example: {'type': 'socks5', 'host': '127.0.0.1', 'port': 1080, 'username': None, 'password': None}
PROXIES = []

# Add proxies from environment variable if set (comma-separated: type:host:port or type:host:port:user:pass)
proxy_env = os.getenv('PROXIES', '')
if proxy_env:
    for p in proxy_env.split(','):
        parts = p.strip().split(':')
        if len(parts) >= 3:
            proxy = {
                'type': parts[0],
                'host': parts[1],
                'port': int(parts[2]),
                'username': parts[3] if len(parts) > 3 else None,
                'password': parts[4] if len(parts) > 4 else None
            }
            PROXIES.append(proxy)
