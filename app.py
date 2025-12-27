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
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        context = browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        try:
            # معالجة الكوكيز
            cookies = json.loads(raw_cookies_text.strip())
            valid_samesite = ["Strict", "Lax", "None"]
            for c in cookies:
                if "sameSite" in c and c["sameSite"] not in valid_samesite: del c["sameSite"]
                if "expirationDate" in c: c["expirationDate"] = int(float(c["expirationDate"]))
                for k in ["hostOnly", "session", "storeId", "id"]: c.pop(k, None)
            context.add_cookies(cookies)

            page = context.new_page()
            url = f"https://ads.tiktok.com/business/creativecenter/inspiration/topads/pc/en?keyword={keyword}"
            page.goto(url, wait_until="networkidle", timeout=60000)
            
            # الانتظار والتحميل
            page.wait_for_timeout(5000)
            page.mouse.wheel(0, 2000)
            page.wait_for_timeout(3000)

            # سحب البطاقات
            cards = page.locator("[class*='ItemCard'], [class*='CardContainer']").all()
            
            for card in cards[:12]:
                try:
                    # سحب العنوان
                    title_el = card.locator("[class*='title'], h3").first
                    title = title_el.inner_text() if title_el.count() > 0 else "TikTok Ad"
                    
                    # سحب رابط الفيديو (نبحث عن الـ src داخل وسام video)
                    video_el = card.locator("video").first
                    video_url = video_el.get_attribute("src") if video_el.count() > 0 else None
                    
                    if not video_url: continue # إذا لم نجد فيديو ننتقل للتالي

                    ad_data = {
                        "ad_id": str(os.urandom(4).hex()),
                        "title": title[:50] + "...",
                        "video_url": video_url,
                        "keyword": keyword
                    }
                    
                    if ads_collection is not None:
                        ads_collection.update_one({"video_url": video_url}, {"$set": ad_data}, upsert=True)
                    results.append(ad_data)
                except: continue
        finally:
            browser.close()
    return results

@app.route('/')
def index():
    ads = list(ads_collection.find().sort("_id", -1).limit(30)) if ads_collection is not None else []
    return render_template('index.html', ads=ads)

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.json
    res = run_scraper(data.get('cookies'), data.get('keyword', 'Trending'))
    return jsonify({"status": "success", "count": len(res), "ads": res})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
