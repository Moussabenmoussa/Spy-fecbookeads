def run_scraper(raw_cookies_text, keyword):
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
        context = browser.new_context()
        
        # تحويل النص الملصق من الهاتف إلى صيغة كوكيز يفهمها المتصفح
        try:
            if "[" in raw_cookies_text: # إذا كان JSON كامل
                cookies = json.loads(raw_cookies_text)
            else: # إذا كان مجرد نص كوكيز عادي
                cookies = []
                for item in raw_cookies_text.split(';'):
                    if '=' in item:
                        name, value = item.strip().split('=', 1)
                        cookies.append({'name': name, 'value': value, 'domain': '.tiktok.com', 'path': '/'})
            
            context.add_cookies(cookies)
        except Exception as e:
            return {"error": f"خطأ في معالجة الكوكيز: {str(e)}"}

        page = context.new_page()
        # بقية الكود كما هو...
