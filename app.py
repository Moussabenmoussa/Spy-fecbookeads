import os
from flask import Flask, jsonify, request, render_template_string
from pymongo import MongoClient
from playwright.sync_api import sync_playwright
import datetime
import re

app = Flask(__name__)

# --- الاتصال بقاعدة البيانات ---
raw_uri = os.environ.get("MONGO_URI", "")
clean_uri = raw_uri.strip().strip('"').strip("'")

try:
    client = MongoClient(clean_uri)
    db = client['ad_hunter_dz']
    print("✅ تم الاتصال بقاعدة البيانات!")
except Exception as e:
    print(f"❌ خطأ: {e}")

# --- الواجهة (نفس الواجهة الجميلة) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DZ Ad Hunter Pro 🦅</title>
    <style>
        :root { --primary: #007bff; --bg: #f4f7f6; }
        body { font-family: sans-serif; background-color: var(--bg); padding: 20px; text-align: center; }
        .container { max-width: 800px; margin: 0 auto; }
        input { padding: 15px; width: 60%; border-radius: 8px; border: 1px solid #ccc; font-size: 16px; }
        button { padding: 15px 30px; background-color: var(--primary); color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; }
        button:hover { background-color: #0056b3; }
        .card { background: white; padding: 20px; margin: 20px 0; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: right; border-right: 5px solid var(--primary); }
        .card h4 { margin: 0 0 10px 0; color: #333; }
        .card p { color: #555; line-height: 1.6; }
        .status { margin: 20px; font-weight: bold; }
        .loader { display: none; margin: 20px auto; border: 4px solid #f3f3f3; border-top: 4px solid #3498db; border-radius: 50%; width: 30px; height: 30px; animation: spin 1s linear infinite; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>
<div class="container">
    <h1>🦅 DZ Ad Hunter <span style="color:var(--primary)">Pro</span></h1>
    <div>
        <input type="text" id="keyword" placeholder="اكتب كلمة واحدة فقط (مثلاً: ساعة)...">
        <button onclick="startScan()" id="searchBtn">بحث</button>
    </div>
    <div class="loader" id="loader"></div>
    <p class="status" id="statusMsg"></p>
    <div id="results"></div>
</div>
<script>
    async function startScan() {
        const keyword = document.getElementById('keyword').value;
        const btn = document.getElementById('searchBtn');
        const loader = document.getElementById('loader');
        const status = document.getElementById('statusMsg');
        const resultsDiv = document.getElementById('results');

        if (!keyword) return;

        btn.disabled = true;
        loader.style.display = "block";
        status.innerText = "جاري البحث في فيسبوك... (انتظر 40 ثانية)";
        resultsDiv.innerHTML = "";

        try {
            const response = await fetch(`/scan?q=${keyword}`);
            const json = await response.json();

            if (json.status === "success" && json.data.results.length > 0) {
                status.innerText = `✅ تم العثور على ${json.data.ads_count} نتائج!`;
                json.data.results.forEach(ad => {
                    resultsDiv.innerHTML += `
                        <div class="card">
                            <h4>${ad.id_text || 'إعلان بدون عنوان'}</h4>
                            <p>${ad.full_text}</p>
                        </div>
                    `;
                });
            } else {
                status.innerText = `⚠️ ${json.data ? json.data.msg : 'لم يتم العثور على نتائج (ربما حظر مؤقت أو كلمة خاطئة)'}`;
            }
        } catch (err) {
            status.innerText = "❌ حدث خطأ في الاتصال (502). حاول بكلمة أخرى.";
        } finally {
            btn.disabled = false;
            loader.style.display = "none";
        }
    }
</script>
</body>
</html>
"""

def hunt_dz_ads(keyword):
    print(f"🇩🇿 جاري البحث (وضع المصفاة الواسعة) عن: {keyword}...")
    
    with sync_playwright() as p:
        # إعدادات المتصفح
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        )
        # نستخدم حجم شاشة ديسك توب لضمان ظهور النصوص بشكل كامل
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()

        # حظر الصور لتسريع العملية (لأننا نريد التأكد من النصوص أولاً)
        page.route("**/*", lambda route: route.abort() 
                   if route.request.resource_type in ["image", "media", "font"] 
                   else route.continue_())

        try:
            # رابط البحث
            url = f"https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=DZ&q={keyword}"
            page.goto(url, timeout=60000)
            
            # ننتظر ظهور أي شيء في الصفحة
            page.wait_for_timeout(5000)

            # --- التغيير الجذري هنا: المصفاة الواسعة ---
            ads_data = page.evaluate("""() => {
                const results = [];
                // نبحث عن كل الـ DIVs
                const divs = Array.from(document.querySelectorAll('div'));
                
                // نبحث عن الـ DIV الذي يحتوي على كلمة "ID:" لأنها موجودة في كل إعلان 100%
                // هذا أضمن طريقة لالتقاط الإعلانات
                const adCards = divs.filter(d => d.innerText.includes('ID:') && d.innerText.length > 50 && d.innerText.length < 1000);

                // نأخذ أول 5 نتائج فريدة
                const uniqueTexts = new Set();
                const finalAds = [];

                for (const card of adCards) {
                    if (!uniqueTexts.has(card.innerText)) {
                        uniqueTexts.add(card.innerText);
                        finalAds.push({
                            text: card.innerText,
                            id_marker: "إعلان نشط"
                        });
                    }
                    if (finalAds.length >= 5) break;
                }
                
                return finalAds;
            }""")
            
            cleaned_ads = []
            for item in ads_data:
                cleaned_ads.append({
                    "full_text": item['text'][:300] + "...", # نعرض أول 300 حرف
                    "id_text": "🔥 نتيجة بحث ناجحة"
                })

            scan_result = {
                "keyword": keyword,
                "ads_count": len(cleaned_ads),
                "results": cleaned_ads,
                "msg": "تم البحث"
            }
            
            # إذا كانت القائمة فارغة، نعيد رسالة توضيحية
            if len(cleaned_ads) == 0:
                scan_result['msg'] = "تم الدخول ولكن لم نلتقط نصوصاً (جرب كلمة عامة مثل: توصيل)"

            return {"status": "success", "data": scan_result}

        except Exception as e:
            return {"status": "error", "error": str(e)}
        finally:
            browser.close()

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/scan', methods=['GET'])
def scan_endpoint():
    query = request.args.get('q', 'Livraison')
    return jsonify(hunt_dz_ads(query))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
