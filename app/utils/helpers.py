from user_agents import parse

# --- 1. الغسالة الشبح (V9) ---
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
            window.location.replace("{target_url}");
        </script>
    </body>
    </html>
    '''

# --- 2. نظام الذكاء (تحليل الزائر) ---
def analyze_visitor(user_agent_string):
    """
    تقوم هذه الدالة بتحليل بصمة الزائر وإرجاع تقرير كامل:
    - هل هو بوت؟ وما اسمه؟
    - نوع الجهاز (Mobile/PC)
    - نظام التشغيل (Android/iOS)
    """
    ua = parse(user_agent_string)
    
    # أ. كشف البوتات بدقة
    bot_name = None
    if ua.is_bot:
        # محاولة معرفة اسم البوت الشهير
        ua_str = user_agent_string.lower()
        if 'facebook' in ua_str: bot_name = 'Facebook Bot'
        elif 'tiktok' in ua_str: bot_name = 'TikTok Bot'
        elif 'google' in ua_str: bot_name = 'Google Bot'
        elif 'twitter' in ua_str: bot_name = 'Twitter Bot'
        elif 'telegram' in ua_str: bot_name = 'Telegram Bot'
        elif 'whatsapp' in ua_str: bot_name = 'WhatsApp Bot'
        else: bot_name = 'Generic Bot'
    
    # ب. كشف الجهاز
    device_type = "Desktop"
    if ua.is_mobile: device_type = "Mobile"
    elif ua.is_tablet: device_type = "Tablet"
    
    return {
        "is_bot": ua.is_bot,
        "bot_name": bot_name,
        "browser": ua.browser.family,
        "os": ua.os.family, # Android, iOS, Windows
        "device": device_type
    }
