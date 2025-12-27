import os
import json
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# --- إصلاح مشكلة الاتصال بقاعدة البيانات ---
MONGO_URI = os.getenv("MONGO_URI", "").strip() # .strip() تحذف أي مسافات زائدة تلقائياً

try:
    if not MONGO_URI:
        raise ValueError("MONGO_URI is missing from environment variables")
    
    # محاولة الاتصال
    client = MongoClient(MONGO_URI)
    db = client['tiktok_spy_db']
    ads_collection = db['ads']
    # اختبار الاتصال البسيط
    client.admin.command('ping')
    print("✅ تم الاتصال بقاعدة البيانات بنجاح")
except Exception as e:
    print(f"❌ خطأ في الاتصال بقاعدة البيانات: {e}")
    # سنترك التطبيق يعمل حتى لو فشلت القاعدة لكي لا ينهار السيرفر
    ads_collection = None

def run_scraper(raw_cookies_text, keyword):
    results = []
    with sync_playwright() as p:
        # إعدادات المتصفح للعمل على السيرفر
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        context = browser.new_context()
        
        try:
            # تنظيف وتحويل الكوكيز
            raw_cookies_text = raw_cookies_text.strip()
            if "[" in raw_cookies_text:
                cookies = json.loads(raw_cookies_text)
            else:
                cookies = []
                for item in raw_cookies_text.split(';'):
                    if '=' in item:
                        name, value = item.strip().split('=', 1)
                        cookies.append({'name': name, 'value': value, 'domain': '.tiktok.com', 'path': '/'})
            
            context.add_cookies(cookies)
        except Exception as e:
            return {"error": f"صيغة الكوكيز غير صحيحة: {str(e)}"}

        page = context.new_page()
        search_url = f"https://ads.tiktok.com/business/creativecenter/inspiration/topads/pc/en?keyword={keyword}"
        
        try:
            page.goto(search_url, wait_until="networkidle", timeout=60000)
            page.mouse.wheel(0, 2000)
            page.wait_for_timeout(3000)

            cards = page.locator(".item-card-V2").all()
            for card in cards[:10]:
                try:
                    ad_id = card.get_attribute("id") or "unknown"
                    title = card.locator(".title-content").inner_text() if card.locator(".title-content").count() > 0 else "No Title"
                    ad_data = {"ad_id": ad_id, "title": title, "keyword": keyword}
                    
                    if ads_collection is not None:
                        ads_collection.update_one({"ad_id": ad_id}, {"$set": ad_data}, upsert=True)
                    results.append(ad_data)
                except: continue
        except Exception as e:
            return {"error": f"فشل في سحب البيانات: {str(e)}"}
        finally:
            browser.close()
            
    return results

@app.route('/')
def index():
    saved_ads = []
    if ads_collection is not None:
        saved_ads = list(ads_collection.find().sort("_id", -1).limit(20))
    return render_template('index.html', ads=saved_ads)

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.json
    cookies = data.get('cookies')
    keyword = data.get('keyword', 'kitchen')
    if not cookies:
        return jsonify({"status": "error", "message": "يرجى لصق الكوكيز"})
    
    new_ads = run_scraper(cookies, keyword)
    if isinstance(new_ads, dict) and "error" in new_ads:
        return jsonify({"status": "error", "message": new_ads["error"]})
    return jsonify({"status": "success", "count": len(new_ads), "ads": new_ads})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
