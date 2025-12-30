import random
from flask import request

# --- 🔥 الغسالة الشبح (V9 Ghost Protocol) ---
# الوظيفة: إخفاء المصدر (Referrer) وجعل الزيارة Direct
def get_laundry_html(target_url):
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <!-- القفل الأول: أمر المتصفح بعدم إرسال المصدر -->
        <meta name="referrer" content="no-referrer">
        <title>Loading...</title>
        <style>body{{background:#fff;}}</style>
    </head>
    <body>
        <script>
            // القفل الثاني: تقنية الاستبدال (Replace)
            // هذه التقنية لا تحفظ الصفحة الحالية في التاريخ (History)
            // مما يجبر المتصفح على نسيان أن الزائر جاء من منصتك
            window.location.replace("{target_url}");
        </script>
    </body>
    </html>
    '''

# --- كشف البوتات (Security) ---
BOT_AGENTS = [
    "facebookexternalhit", "Facebot", "Twitterbot", "LinkedInBot",
    "WhatsApp", "TelegramBot", "Googlebot", "AdsBot", "crawler",
    "curl", "wget", "python-requests"
]

def is_bot(user_agent):
    if not user_agent: return True
    user_agent = user_agent.lower()
    for bot in BOT_AGENTS:
        if bot.lower() in user_agent:
            return True
    return False
