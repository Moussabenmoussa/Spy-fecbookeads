import os
from flask import Flask, jsonify, request, render_template_string
from pymongo import MongoClient
from playwright.sync_api import sync_playwright
import datetime
import re

app = Flask(__name__)

# --- إعدادات قاعدة البيانات ---
raw_uri = os.environ.get("MONGO_URI", "")
clean_uri = raw_uri.strip().strip('"').strip("'")

try:
    client = MongoClient(clean_uri)
    db = client['ad_hunter_dz']
    ads_col = db['dz_winners']
    print("✅ تم الاتصال بقاعدة البيانات!")
except Exception as e:
    print(f"❌ خطأ في الاتصال: {e}")

# --- واجهة الموقع (HTML + CSS + JS) ---
# وضعناها هنا لتسهيل النسخ واللصق في ملف واحد
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DZ Ad Hunter Pro 🦅</title>
    <style>
        :root { --primary: #007bff; --bg: #f4f7f6; --card-bg: #ffffff; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: var(--bg); margin: 0; padding: 20px; color: #333; }
        .container { max-width: 800px; margin: 0 auto; text-align: center; }
        
        h1 { color: #2c3e50; margin-bottom: 30px; }
        .search-box { display: flex; gap: 10px; justify-content: center; margin-bottom: 40px; }
        input { padding: 15px; width: 60%; border: 1px solid #ddd; border-radius: 8px; font-size: 16px; outline: none; }
        button { padding: 15px 30px; background-color: var(--primary); color: white; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; transition: 0.3s; }
        button:hover { background-color: #0056b3; }
        button:disabled { background-color: #ccc; cursor: not-allowed; }

        .loader { display: none; margin: 20px auto; border: 5px solid #f3f3f3; border-top: 5px solid var(--primary); border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

        .results-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; text-align: right; }
        .card { background: var(--card-bg); padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: transform 0.2s; border-right: 5px solid var(--primary); }
        .card:hover { transform: translateY(-5px); }
        .card h3 { margin-top: 0; color: #333; font-size: 18px; }
        .phone-badge { background: #e1f5fe; color: #0288d1; padding: 5px 10px; border-radius: 15px; font-weight: bold; font-size: 14px; display: inline-block; margin-bottom: 10px; }
        .card p { color: #666; font-size: 14px; line-height: 1.6; }
        .status-msg { margin-top: 20px; font-weight: bold; color: #555; }
    </style>
</head>
<body>

<div class="container">
    <h1>🦅 DZ Ad Hunter <span style="color:#007bff">Pro</span></h1>
    
    <div class="search-box">
        <input type="text" id="keyword" placeholder="اكتب المنتج (مثلاً: ساعة، توصيل، تخفيض)...">
        <button onclick="startScan()" id="searchBtn">بحث الآن</button>
    </div>

    <div class="loader" id="loader"></div>
    <p class="status-msg" id="statusMsg"></p>

    <div class="results-grid" id="results"></div>
</div>

<script>
    async function startScan() {
        const keyword = document.getElementById('keyword').value;
        const btn = document.getElementById('searchBtn');
        const loader = document.getElementById('loader');
        const status = document.getElementById('statusMsg');
        const resultsDiv = document.getElementById('results');

        if (!keyword) { alert("اكتب شيئاً للبحث!"); return; }

        // تجهيز الواجهة
        btn.disabled = true;
        btn.innerText = "جاري القنص...";
        loader.style.display = "block";
        status.innerText = "الروبوت يبحث في فيسبوك الآن (قد يستغرق 30-60 ثانية)...";
        resultsDiv.innerHTML = "";

        try {
            // طلب البيانات من الباك-إند
            const response = await fetch(`/scan?q=${keyword}`);
            const json = await response.json();

            if (json.status === "success") {
                status.innerText = `✅ تم العثور على ${json.data.ads_count} إعلانات ناجحة!`;
                
                json.data.results.forEach(ad => {
                    const card = document.createElement('div');
                    card.className = 'card';
                    card.innerHTML = `
                        <span class="phone-badge">📞 ${ad.phone_found}</span>
                        <h3>إعلان ${keyword}</h3>
                        <p>${ad.full_text}</p>
                    `;
                    resultsDiv.appendChild(card);
                });
            } else {
                status.innerText = "⚠️ لم يتم العثور على نتائج، أو حدث خطأ بسيط.";
            }

        } catch (err) {
            status.innerText = "❌ حدث خطأ في الاتصال بالسيرفر.";
            console.error(err);
        } finally {
            btn.disabled = false;
            btn.innerText = "بحث الآن";
            loader.style.display = "none";
        }
    }
</script>

</body>
</html>
"""

def hunt_dz_ads(keyword):
    country = "DZ"
    print(f"🇩🇿 جاري البحث عن: {keyword}...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        )
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36'
        )
        page = context.new_page()

        # تسريع التصفح
        page.route("**/*", lambda route: route.abort() 
                   if route.request.resource_type in ["image", "media", "font"] 
                   else route.continue_())

        try:
            url = f"https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country={country}&q={keyword}"
            page.goto(url, timeout=60000)
            
            # ننتظر قليلاً
            try:
                page.wait_for_selector('div[role="main"]', timeout=20000)
            except:
                return {"status": "empty", "msg": "No results"}

            # استخراج البيانات
            ads_data = page.evaluate("""() => {
                const elements = Array.from(document.querySelectorAll('div'));
                const cards = elements.filter(e => 
                    (e.innerText.includes('05') || e.innerText.includes('06') || e.innerText.includes('07') || e.innerText.includes('DA')) 
                    && e.innerText.length > 50 && e.innerText.length < 600
                );
                const uniqueCards = [...new Set(cards.map(c => c.innerText))];
                return uniqueCards.slice(0, 4); 
            }""")
            
            cleaned_ads = []
            for text in ads_data:
                phone = re.search(r'(0[567]\d{8})', text.replace(" ", ""))
                cleaned_ads.append({
                    "full_text": text[:150] + "...", 
                    "phone_found": phone.group(1) if phone else "يوجد بالسجل",
                })

            return {
                "status": "success", 
                "data": {
                    "ads_count": len(cleaned_ads),
                    "results": cleaned_ads
                }
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}
        finally:
            browser.close()

# --- المسارات ---

@app.route('/')
def index():
    # الآن الصفحة الرئيسية تعرض الواجهة الاحترافية بدلاً من النص
    return render_template_string(HTML_TEMPLATE)

@app.route('/scan', methods=['GET'])
def scan_endpoint():
    query = request.args.get('q', 'Livraison')
    return jsonify(hunt_dz_ads(query))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
