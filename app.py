import os
from flask import Flask, jsonify, request
from pymongo import MongoClient
from playwright.sync_api import sync_playwright
import datetime
import re # مكتبة للبحث عن أرقام الهواتف

app = Flask(__name__)

# --- إعدادات قاعدة البيانات ---
raw_uri = os.environ.get("MONGO_URI", "")
clean_uri = raw_uri.strip().strip('"').strip("'")

try:
    client = MongoClient(clean_uri)
    db = client['ad_hunter_dz'] # غيرنا اسم القاعدة لتكون خاصة بالجزائر
    ads_col = db['dz_winners']
    print(f"✅ تم الاتصال بقاعدة البيانات الجزائرية!")
except Exception as e:
    print(f"❌ خطأ في الاتصال: {e}")

def hunt_dz_ads(keyword):
    # تثبيت الدولة على الجزائر
    country = "DZ"
    print(f"🇩🇿 جاري البحث في الجزائر عن: {keyword}...")
    
    with sync_playwright() as p:
        # إعدادات متصفح خفيفة جداً
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        )
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36'
        )
        page = context.new_page()

        # حظر الصور والفيديو (توفير الرام)
        page.route("**/*", lambda route: route.abort() 
                   if route.request.resource_type in ["image", "media", "font"] 
                   else route.continue_())

        try:
            # رابط البحث المخصص للجزائر
            url = f"https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country={country}&q={keyword}"
            
            page.goto(url, timeout=60000)
            
            # ننتظر ظهور أي نتيجة تحتوي على نص (لتجنب الصفحات الفارغة)
            try:
                page.wait_for_selector('div[role="main"]', timeout=20000)
            except:
                return {"status": "empty", "msg": "لم يتم العثور على نتائج أو النتائج بطيئة التحميل"}

            # --- منطق استخراج البيانات الجزائرية ---
            # سنقوم بسحب النصوص والبحث عن أرقام هواتف جزائرية فيها
            ads_data = page.evaluate("""() => {
                const results = [];
                // نأخذ كل العناصر التي تحتوي على نصوص طويلة نوعاً ما (نص الإعلان)
                const elements = Array.from(document.querySelectorAll('div'));
                
                // فلتر ذكي: نأخذ فقط العناصر التي تحتوي على كلمات بيع
                const cards = elements.filter(e => 
                    (e.innerText.includes('05') || e.innerText.includes('06') || e.innerText.includes('07') || e.innerText.includes('DA')) 
                    && e.innerText.length > 50 
                    && e.innerText.length < 600
                );

                // نأخذ أفضل 3 نتائج فقط لتخفيف الحمل
                // Set لإزالة التكرار
                const uniqueCards = [...new Set(cards.map(c => c.innerText))];
                
                return uniqueCards.slice(0, 3); 
            }""")
            
            # تنظيف النتائج في بايثون
            cleaned_ads = []
            for text in ads_data:
                # استخراج رقم الهاتف (Regex)
                phone = re.search(r'(0[567]\d{8})', text.replace(" ", ""))
                cleaned_ads.append({
                    "full_text": text[:200] + "...", # نأخذ أول 200 حرف
                    "phone_found": phone.group(1) if phone else "No Phone",
                    "source": "Facebook Ads DZ"
                })

            scan_result = {
                "keyword": keyword,
                "country": "DZ",
                "scan_date": datetime.datetime.now(),
                "ads_count": len(cleaned_ads),
                "results": cleaned_ads,
                "status": "Success"
            }
            
            if len(cleaned_ads) > 0:
                ads_col.insert_one(scan_result)
            
            return {"status": "success", "data": scan_result}

        except Exception as e:
            return {"status": "error", "error": str(e)}
        finally:
            browser.close()

@app.route('/')
def index():
    return "<h1>🇩🇿 DZ Ad Hunter is Ready</h1>"

@app.route('/scan', methods=['GET'])
def scan_endpoint():
    # إذا لم يكتب المستخدم شيئاً، نبحث عن "توصيل" افتراضياً
    query = request.args.get('q', 'Livraison')
    
    # لم نعد بحاجة لطلب الدولة، هي مثبتة على DZ
    result = hunt_dz_ads(query)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
