import os, json, re
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# --- تنظيف رابط قاعدة البيانات ---
raw_uri = os.getenv("MONGO_URI", "")
MONGO_URI = re.sub(r'[\s\n\r]', '', raw_uri).strip()

try:
    if MONGO_URI:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client.get_database()
        ads_collection = db['ads']
        client.admin.command('ping')
    else:
        ads_collection = None
except:
    ads_collection = None

def run_scraper(raw_cookies_text, keyword):
    results = []
    with sync_playwright() as p:
        # إعداد المتصفح
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        context = browser.new_context()
        
        try:
            raw_cookies_text = raw_cookies_text.strip()
            if "[" in raw_cookies_text:
                cookies = json.loads(raw_cookies_text)
                
                # --- معالجة الكوكيز لتتوافق مع Playwright ---
                valid_samesite = ["Strict", "Lax", "None"]
                for cookie in cookies:
                    # 1. إصلاح SameSite
                    if "sameSite" in cookie:
                        if cookie["sameSite"] not in valid_samesite:
                            # حذف القيمة غير الصحيحة (مثل unspecified) ليستخدم المتصفح الافتراضي
                            del cookie["sameSite"]
                    
                    # 2. تحويل تاريخ الانتهاء إلى رقم صحيح
                    if "expirationDate" in cookie:
                        cookie["expirationDate"] = int(float(cookie["expirationDate"]))
                    
                    # 3. حذف خصائص غير ضرورية قد تسبب مشاكل
                    cookie.pop("hostOnly", None)
                    cookie.pop("session", None)
                    cookie.pop("storeId", None)
                    cookie.pop("id", None)

                context.add_cookies(cookies)
            else:
                # معالجة إذا قام المستخدم بلصق نص عادي
                ck_list = []
                for item in raw_cookies_text.split(';'):
                    if '=' in item:
                        name, value = item.strip().split('=', 1)
                        ck_list.append({'name': name, 'value': value, 'domain': '.tiktok.com', 'path': '/'})
                context.add_cookies(ck_list)

        except Exception as e:
            browser.close()
            return {"error": f"خطأ في الكوكيز: {str(e)}"}

        page = context.new_page()
        # الدخول لصفحة البحث
        search_url = f"https://ads.tiktok.com/business/creativecenter/inspiration/topads/pc/en?keyword={keyword}"
        
        try:
            page.goto(search_url, wait_until="networkidle", timeout=60000)
            # التمرير لأسفل لرؤية الإعلانات
            page.mouse.wheel(0, 3000)
            page.wait_for_timeout(5000)

            # سحب العناصر (الـ Selector الخاص بتيك توك قد يتغير، نستخدم محددات مرنة)
            cards = page.locator("[class*='item-card']").all()
            
            for card in cards[:10]:
                try:
                    title = card.locator("[class*='title']").first.inner_text() if card.locator("[class*='title']").count() > 0 else "Ad"
                    ad_id = card.get_attribute("id") or "N/A"
                    
                    ad_data = {"ad_id": ad_id, "title": title, "keyword": keyword}
                    
                    if ads_collection is not None:
                        ads_collection.update_one({"ad_id": ad_id}, {"$set": ad_data}, upsert=True)
                    results.append(ad_data)
                except: continue
        except Exception as e:
            return {"error": f"خطأ أثناء التصفح: {str(e)}"}
        finally:
            browser.close()
            
    return results

@app.route('/')
def index():
    ads = []
    if ads_collection is not None:
        ads = list(ads_collection.find().sort("_id", -1).limit(20))
    return render_template('index.html', ads=ads)

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.json
    cookies = data.get('cookies')
    keyword = data.get('keyword', 'trending')
    if not cookies:
        return jsonify({"status": "error", "message": "أين الكوكيز؟"})
    
    res = run_scraper(cookies, keyword)
    if isinstance(res, dict) and "error" in res:
        return jsonify({"status": "error", "message": res["error"]})
    return jsonify({"status": "success", "count": len(res), "ads": res})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
