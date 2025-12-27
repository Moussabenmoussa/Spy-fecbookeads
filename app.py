import os, json, re
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# --- 1. تنظيف وإعداد رابط قاعدة البيانات ---
raw_uri = os.getenv("MONGO_URI", "")
MONGO_URI = re.sub(r'[\s\n\r]', '', raw_uri).strip()

try:
    if MONGO_URI:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client.get_database()
        ads_collection = db['ads']
        client.admin.command('ping')
        print("✅ MongoDB Connected Successfully")
    else:
        print("⚠️ No MONGO_URI found, ads will not be saved.")
        ads_collection = None
except Exception as e:
    print(f"❌ DB Connection Error: {e}")
    ads_collection = None

# --- 2. دالة السحب (Scraper) ---
def run_scraper(raw_cookies_text, keyword):
    results = []
    with sync_playwright() as p:
        # تشغيل المتصفح مع إعدادات تخطي الحظر
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        
        try:
            # تنظيف ومعالجة الكوكيز القادمة من الهاتف
            raw_cookies_text = raw_cookies_text.strip()
            if "[" in raw_cookies_text:
                cookies = json.loads(raw_cookies_text)
                valid_samesite = ["Strict", "Lax", "None"]
                for cookie in cookies:
                    # إصلاح مشكلة SameSite
                    if "sameSite" in cookie and cookie["sameSite"] not in valid_samesite:
                        del cookie["sameSite"]
                    # إصلاح مشكلة تاريخ الانتهاء
                    if "expirationDate" in cookie:
                        try:
                            cookie["expirationDate"] = int(float(cookie["expirationDate"]))
                        except: del cookie["expirationDate"]
                    # حذف الخصائص غير المتوافقة مع Playwright
                    for key in ["hostOnly", "session", "storeId", "id"]:
                        cookie.pop(key, None)
                context.add_cookies(cookies)
            
            page = context.new_page()
            # الرابط المباشر للبحث في تيك توك
            search_url = f"https://ads.tiktok.com/business/creativecenter/inspiration/topads/pc/en?keyword={keyword}"
            print(f"🚀 Searching for: {keyword}")
            
            page.goto(search_url, wait_until="networkidle", timeout=60000)
            
            # الانتظار حتى تظهر عناصر الإعلانات
            try:
                page.wait_for_selector("[class*='Card']", timeout=15000)
            except: pass

            # سكرول لأسفل لتحميل المزيد
            page.mouse.wheel(0, 2000)
            page.wait_for_timeout(3000)

            # استخراج البطاقات باستخدام محددات مرنة
            cards = page.locator("[class*='ItemCard'], [class*='CardContainer'], [class*='card-V2']").all()
            print(f"📦 Found {len(cards)} elements")

            for card in cards[:12]:
                try:
                    # محاولة استخراج العنوان أو نص الإعلان
                    title_el = card.locator("[class*='title'], [class*='desc'], h3").first
                    title = title_el.inner_text() if title_el.count() > 0 else "TikTok Ad"
                    
                    # محاولة استخراج ID فريد
                    ad_id = card.get_attribute("id") or str(abs(hash(title)))
                    
                    ad_data = {
                        "ad_id": ad_id,
                        "title": title[:100], # تقصير النص
                        "keyword": keyword
                    }
                    
                    # حفظ في MongoDB
                    if ads_collection is not None:
                        ads_collection.update_one({"ad_id": ad_id}, {"$set": ad_data}, upsert=True)
                    
                    results.append(ad_data)
                except: continue

        except Exception as e:
            print(f"❌ Scraper Error: {e}")
            return {"error": str(e)}
        finally:
            browser.close()
            
    return results

# --- 3. المسارات (Routes) ---
@app.route('/')
def index():
    saved_ads = []
    if ads_collection is not None:
        try:
            saved_ads = list(ads_collection.find().sort("_id", -1).limit(24))
        except: pass
    return render_template('index.html', ads=saved_ads)

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.json
    cookies = data.get('cookies')
    keyword = data.get('keyword', 'Kitchen')
    
    if not cookies:
        return jsonify({"status": "error", "message": "يرجى لصق الكوكيز أولاً"})
    
    new_ads = run_scraper(cookies, keyword)
    
    if isinstance(new_ads, dict) and "error" in new_ads:
        return jsonify({"status": "error", "message": new_ads["error"]})
    
    return jsonify({"status": "success", "count": len(new_ads), "ads": new_ads})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
