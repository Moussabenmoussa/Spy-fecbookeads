import os
from flask import Flask, jsonify, request
from pymongo import MongoClient
from playwright.sync_api import sync_playwright
import datetime
import random
import time

app = Flask(__name__)

# --- 1. الإعدادات (من Render) ---
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/ad_hunter")
client = MongoClient(MONGO_URI)
db = client['ad_hunter_db']
ads_col = db['winning_ads']

# --- 2. الروبوت القناص (The Hunter Logic) ---
def hunt_facebook_ads(keyword="Paiement à la livraison", country="DZ"):
    print(f"🕵️ بدء البحث عن: {keyword} في {country}...")
    
    found_ads = []
    
    with sync_playwright() as p:
        # تشغيل متصفح خفي مع تمويه (Stealth Mode بسيط)
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            viewport={'width': 1280, 'height': 800}
        )
        page = context.new_page()
        
        # رابط مكتبة إعلانات فيسبوك المباشر
        # active_status=active : نبحث عن الإعلانات النشطة فقط (لأنها الرابحة)
        url = f"https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country={country}&q={keyword}"
        
        try:
            page.goto(url, timeout=60000)
            page.wait_for_timeout(5000) # انتظار التحميل
            
            # محاولة العثور على كروت الإعلانات (Selectors تتغير دائماً، لذا نستخدم طريقة عامة)
            # هنا سنقوم بسكرول بسيط لتحميل المزيد
            for _ in range(3):
                page.mouse.wheel(0, 1000)
                page.wait_for_timeout(2000)
            
            # التقاط البيانات (هنا نستخدم لقطة شاشة للنتائج كبداية لضمان العمل)
            # في النسخة المتقدمة نستخرج النصوص div by div
            screenshot_bytes = page.screenshot(full_page=False)
            
            # تخزين "جلسة البحث" كدليل
            scan_id = ads_col.insert_one({
                "keyword": keyword,
                "country": country,
                "scan_date": datetime.datetime.now(),
                "status": "Success",
                "result_count": "Unknown (Screenshot Taken)" 
                # ملاحظة: في النسخة 2.0 سنضيف تحليل HTML دقيق لاستخراج عدد الإعلانات
            }).inserted_id
            
            print("✅ تمت عملية المسح بنجاح!")
            return {"status": "success", "scan_id": str(scan_id), "msg": "تم مسح المكتبة وتخزين النتائج"}

        except Exception as e:
            print(f"❌ خطأ أثناء البحث: {e}")
            return {"status": "error", "error": str(e)}
            
        finally:
            browser.close()

# --- 3. المسارات (Routes) ---

@app.route('/')
def index():
    return "<h1>🦅 Ad Hunter is Running...</h1><p>Use /scan?q=shoes endpoint to start hunting.</p>"

@app.route('/scan', methods=['GET'])
def scan_endpoint():
    # مثال للاستخدام: website.com/scan?q=شحن مجاني
    query = request.args.get('q', 'Paiement à la livraison')
    country = request.args.get('country', 'DZ')
    
    result = hunt_facebook_ads(query, country)
    return jsonify(result)

@app.route('/results', methods=['GET'])
def get_results():
    # جلب آخر عمليات البحث من قاعدة البيانات
    scans = list(ads_col.find({}, {'_id': 0}).sort("scan_date", -1).limit(10))
    return jsonify(scans)

if __name__ == '__main__':
    # تشغيل السيرفر
    app.run(host='0.0.0.0', port=10000)
