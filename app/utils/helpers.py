import random
import requests
from flask import request

# --- 🔥 الغسالة الذهبية (V9) ---
# هذا هو الكود الذي أعطاك Referrer: Empty
def get_laundry_html(target_url):
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="referrer" content="no-referrer">
        <title>Loading...</title>
        <style>body{{background:#fff;}}</style>
    </head>
    <body>
        <script>
            // التقنية: استبدال التاريخ + منع الإحالة
            window.location.replace("{target_url}");
        </script>
    </body>
    </html>
    '''

# --- كشف البوتات ---
BOT_AGENTS = [
    "facebookexternalhit", "Facebot", "Twitterbot", "LinkedInBot",
    "WhatsApp", "TelegramBot", "Googlebot", "AdsBot", "crawler"
]

def is_bot(user_agent):
    if not user_agent: return True
    for bot in BOT_AGENTS:
        if bot.lower() in user_agent.lower():
            return True
    return False
