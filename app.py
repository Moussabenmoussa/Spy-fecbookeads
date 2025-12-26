
import os
from flask import Flask, jsonify, request
from pymongo import MongoClient
from playwright.sync_api import sync_playwright
import datetime

app = Flask(__name__)

# --- تصحيح الرابط أوتوماتيكياً ---
# هذا السطر يمسح المسافات الزائدة ويعالج الرابط
raw_uri = os.environ.get("MONGO_URI", "")
clean_uri = raw_uri.strip().strip('"').strip("'")

# الاتصال بقاعدة البيانات
try:
    client = MongoClient(clean_uri)
    db = client['ad_hunter_db']
    ads_col = db['winning_ads']
    # تجربة اتصال سريعة للتأكد
    client.server_info()
    print("✅ تم الاتصال بقاعدة البيانات بنجاح!")
except Exception as e:
    print(f"❌ خطأ في قاعدة البيانات: {e}")

def hunt_facebook_ads(keyword, country="DZ"):
    print(f"🕵️ بدء البحث السريع عن: {keyword}...")
    
    with sync_playwright() as p:
        # تشغيل المتصفح بوضع توفير الموارد الأقصى
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu'
            ]
        )
        context = browser.new_context()
        page = context.new_page()

        # منع تحميل الصور والفيديو والخطوط (تسريع 100%)
        page.route("**/*", lambda route: route.abort() 
                   if route.request.resource_type in ["image", "media", "font", "stylesheet"] 
                   else route.continue_())

        try:
            # استخدام رابط الموبايل (أخف)
            url = f"https://m.facebook.com/ads/library/?active_status=active&ad_type=all&country={country}&q={keyword}"
            
            # وقت انتظار 60 ثانية
            page.goto(url, timeout=60000)
            page.wait_for_timeout(2000)
            
            page_title = page.title()
            
            scan_data = {
                "keyword": keyword,
                "scan_date": datetime.datetime.now(),
                "status": "Success",
                "page_title": page_title,
                "note": "تم (وضع توفير الذاكرة)"
            }
            
            # حفظ فقط إذا كان الاتصال سليماً
            if 'ads_col' in globals():
                ads_col.insert_one(scan_data)
            
            return {"status": "success", "data": scan_data}

        except Exception as e:
            return {"status": "error", "error": str(e)}
        finally:
            browser.close()

@app.route('/')
def index():
    return "<h1>🦅 Ad Hunter is Ready (Fix Applied)</h1>"

@app.route('/scan', methods=['GET'])
def scan_endpoint():
    query = request.args.get('q', 'Paiement à la livraison')
    country = request.args.get('country', 'DZ')
    result = hunt_facebook_ads(query, country)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
