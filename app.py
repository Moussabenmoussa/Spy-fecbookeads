import os
from flask import Flask, jsonify, request
from pymongo import MongoClient
from playwright.sync_api import sync_playwright
import datetime

app = Flask(__name__)

# الإعدادات
MONGO_URI = os.environ.get("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client['ad_hunter_db']
ads_col = db['winning_ads']

def hunt_facebook_ads(keyword, country="DZ"):
    print(f"🕵️ بدء البحث السريع عن: {keyword}...")
    
    with sync_playwright() as p:
        # تشغيل المتصفح بوضع توفير الموارد
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage', # مهم جداً للدوكر
                '--disable-gpu'
            ]
        )
        page = browser.new_page()

        # --- السر: منع تحميل الصور والخطوط لتوفير الذاكرة ---
        page.route("**/*", lambda route: route.abort() 
                   if route.request.resource_type in ["image", "media", "font"] 
                   else route.continue_())

        try:
            # استخدام رابط فيسبوك الموبايل (أخف وأسرع)
            url = f"https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country={country}&q={keyword}"
            
            # زيادة وقت الانتظار لـ 60 ثانية
            page.goto(url, timeout=60000, wait_until="domcontentloaded")
            
            # انتظار بسيط
            page.wait_for_timeout(3000)
            
            # أخذ العنوان كدليل على النجاح (بدل لقطة الشاشة الثقيلة حالياً)
            page_title = page.title()
            
            # تخزين النتيجة
            scan_data = {
                "keyword": keyword,
                "scan_date": datetime.datetime.now(),
                "status": "Success",
                "page_title": page_title,
                "note": "تم البحث بنجاح (وضع توفير الذاكرة)"
            }
            ads_col.insert_one(scan_data)
            
            return {"status": "success", "data": scan_data}

        except Exception as e:
            return {"status": "error", "error": str(e)}
        finally:
            browser.close()

@app.route('/')
def index():
    return "<h1>🦅 Ad Hunter Lite is Ready!</h1>"

@app.route('/scan', methods=['GET'])
def scan_endpoint():
    query = request.args.get('q', 'Paiement à la livraison')
    country = request.args.get('country', 'DZ')
    result = hunt_facebook_ads(query, country)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
