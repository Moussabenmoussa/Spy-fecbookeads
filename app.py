import os
import json
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# إعداد MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017") # ضع رابطك هنا أو في Env
client = MongoClient(MONGO_URI)
db = client['tiktok_spy_db']
ads_collection = db['ads']

def run_scraper(cookies_json, keyword):
    results = []
    with sync_playwright() as p:
        # إعدادات المتصفح للعمل على السيرفر
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        context = browser.new_context()
        
        # إضافة الكوكيز لتخطي تسجيل الدخول
        try:
            cookies = json.loads(cookies_json)
            context.add_cookies(cookies)
        except Exception as e:
            return {"error": "صيغة الكوكيز غير صحيحة"}

        page = context.new_page()
        # الدخول لصفحة البحث مباشرة
        search_url = f"https://ads.tiktok.com/business/creativecenter/inspiration/topads/pc/en?keyword={keyword}"
        
        page.goto(search_url, wait_until="networkidle", timeout=60000)
        
        # التمرير لأسفل قليلاً لتحميل النتائج
        page.mouse.wheel(0, 2000)
        page.wait_for_timeout(3000)

        # سحب الإعلانات (Selectors قد تحتاج تحديث بسيط حسب تحديثات تيك توك)
        cards = page.locator(".item-card-V2").all()
        
        for card in cards[:10]: # سحب أول 10 إعلانات
            try:
                ad_id = card.get_attribute("id") or "unknown"
                title = card.locator(".title-content").inner_text() if card.locator(".title-content").count() > 0 else "No Title"
                
                ad_data = {
                    "ad_id": ad_id,
                    "title": title,
                    "keyword": keyword,
                    "timestamp": os.sys.prefix # للتميز فقط
                }
                
                # حفظ في MongoDB
                ads_collection.update_one({"ad_id": ad_id}, {"$set": ad_data}, upsert=True)
                results.append(ad_data)
            except:
                continue

        browser.close()
    return results

@app.route('/')
def index():
    # جلب آخر الإعلانات المحفوظة من القاعدة
    saved_ads = list(ads_collection.find().sort("_id", -1).limit(20))
    return render_template('index.html', ads=saved_ads)

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.json
    cookies = data.get('cookies')
    keyword = data.get('keyword', 'kitchen')
    
    if not cookies:
        return jsonify({"status": "error", "message": "يرجى لصق الكوكيز أولاً"})
    
    try:
        new_ads = run_scraper(cookies, keyword)
        if "error" in new_ads:
            return jsonify({"status": "error", "message": new_ads["error"]})
        return jsonify({"status": "success", "count": len(new_ads), "ads": new_ads})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
