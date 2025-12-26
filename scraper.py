from playwright.sync_api import sync_playwright
import json

def scrape_tiktok(cookies_json, search_term):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # إضافة الكوكيز للجلسة
        context = browser.new_context()
        context.add_cookies(json.loads(cookies_json))
        
        page = context.new_page()
        url = f"https://ads.tiktok.com/business/creativecenter/inspiration/topads/pc/en?keyword={search_term}"
        page.goto(url, wait_until="networkidle")

        # منطق سحب البيانات (مثال مبسط)
        ads = []
        ad_cards = page.locator(".item-card").all() # تأكد من Selector الصحيح
        
        for card in ad_cards[:10]: # سحب أول 10
            data = {
                "ad_id": card.get_attribute("data-ad-id"), # افتراضي
                "title": card.locator(".title").inner_text(),
                "video_url": card.locator("video").get_attribute("src")
            }
            ads.append(data)
        
        browser.close()
        return ads
