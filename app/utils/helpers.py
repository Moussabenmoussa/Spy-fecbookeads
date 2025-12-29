import urllib.parse
from urllib.parse import urlparse

# المعرف الخاص بمحرك بحثك العالمي (SaaS Engine)
GOOGLE_CSE_ID = "b797437107d6140cd" 

def get_laundry_html(target_url):
    # --- SaaS Organic Simulator (Multi-Tenant V5) ---
    # هذا النظام يعمل مع أي عميل.
    # الفكرة: نستخرج دومين العميل ونبحث عن رابطه حصرياً في جوجل.
    
    # 1. استخراج الدومين من رابط العميل (مثلاً: news-site.com)
    try:
        parsed_uri = urlparse(target_url)
        domain = parsed_uri.netloc 
        # تنظيف الدومين (إزالة www. إذا وجدت لضمان دقة البحث)
        if domain.startswith("www."):
            domain = domain[4:]
    except:
        domain = "" # احتياط في حالة الرابط المعطوب

    # 2. بناء استعلام البحث الدقيق (Magic Query)
    # الصيغة: site:domain.com "الرابط كاملاً"
    # هذا يجبر جوجل على تجاهل كل شيء وإظهار هذه الصفحة فقط.
    if domain:
        search_query = f'site:{domain} "{target_url}"'
    else:
        # في حال فشل استخراج الدومين، نبحث عن الرابط مباشرة
        search_query = f'"{target_url}"'
        
    encoded_query = urllib.parse.quote(search_query)
    
    # 3. تكوين رابط المحرك
    google_search_url = f"https://cse.google.com/cse?cx={GOOGLE_CSE_ID}&q={encoded_query}"
    
    # 4. صفحة البوابة الأمنية (Security Gateway)
    # تصميم احترافي يوحي بالثقة ويطلب من الزائر "التحقق"
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="referrer" content="no-referrer">
        <title>Security Checkpoint</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #f8f9fa; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; color: #3c4043; }}
            .card {{ background: #fff; padding: 48px; border-radius: 8px; box-shadow: 0 1px 3px rgba(60,64,67,0.3), 0 4px 8px 3px rgba(60,64,67,0.15); text-align: center; max-width: 400px; width: 90%; }}
            .shield-icon {{ width: 64px; height: 64px; fill: #1a73e8; margin-bottom: 24px; }}
            h1 {{ font-size: 24px; font-weight: 400; margin: 0 0 16px 0; color: #202124; }}
            p {{ font-size: 14px; line-height: 1.5; color: #5f6368; margin: 0 0 32px 0; }}
            .btn {{ background-color: #1a73e8; color: #fff; font-weight: 500; font-size: 14px; padding: 12px 24px; border-radius: 4px; text-decoration: none; display: inline-block; transition: background-color .2s box-shadow .2s; border: none; cursor: pointer; }}
            .btn:hover {{ background-color: #1765cc; box-shadow: 0 1px 2px rgba(60,64,67,0.3); }}
            .footer {{ margin-top: 32px; font-size: 12px; color: #70757a; }}
        </style>
    </head>
    <body>
        <div class="card">
            <svg class="shield-icon" viewBox="0 0 24 24"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8z"/></svg>
            <h1>Security Check Required</h1>
            <p>To access the destination URL, please verify your connection request through our secure search gateway.</p>
            
            <a href="{google_search_url}" class="btn">Click to Verify & Continue</a>
            
            <div class="footer">
                Protected by <strong>Google Cloud Armor</strong>
            </div>
        </div>

        <script>
            // تنظيف السجل لمنع العودة
            if (window.history.replaceState) {{
                window.history.replaceState(null, null, window.location.href);
            }}
        </script>
    </body>
    </html>
    '''

def is_bot(user_agent):
    if not user_agent: return True
    # قائمة البوتات المحدثة والشاملة
    BOT_AGENTS = [
        "facebookexternalhit", "Facebot", "Twitterbot", "LinkedInBot",
        "WhatsApp", "TelegramBot", "Googlebot", "AdsBot", "crawler", "curl", "python", "yandex", "bingbot"
    ]
    for bot in BOT_AGENTS:
        if bot.lower() in user_agent.lower():
            return True
    return False
