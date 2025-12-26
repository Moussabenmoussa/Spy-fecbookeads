
import os, re, random
import google.generativeai as genai
from flask import Flask, jsonify, request, render_template_string
from playwright.sync_api import sync_playwright

app = Flask(__name__)

# --- إعدادات Gemini AI المجاني ---
# ملاحظة: إذا توقف AI عن العمل بسبب ضغط الطلبات، سيبقى جلب الإعلانات يعمل بشكل طبيعي
os.environ["GEMINI_API_KEY"] = "AIzaSyDApm1SX0Nz_cuWE0I65t3ydz-wfPloSnM"
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

NICHES = {
    "home": ["Cuisine", "Maison", "Nettoyage", "Décoration", "Outil"],
    "beauty": ["Soins", "Visage", "Cheveux", "Beauté", "Parfum"],
    "tech": ["Montre", "Écouteurs", "Bluetooth", "Chargeur", "Gadget"],
    "kids": ["Jouet", "Bébé", "Enfant", "Éducatif", "Jeu"],
    "fashion": ["Sac", "Chaussures", "Vêtement", "Homme", "Femme"],
    "sports": ["Sport", "Fitness", "Gym", "Running", "Basket"]
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>DZ Ad Hunter Pro</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Cairo', sans-serif; background: #f0f2f5; margin: 0; padding: 10px; color: #1c1e21; }
        .header { text-align: center; padding: 20px 0; }
        .header h1 { margin: 0; font-size: 24px; color: #1877f2; }
        
        .grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 20px; }
        .btn { 
            background: #fff; border: 1px solid #dddfe2; border-radius: 10px; padding: 15px;
            font-size: 16px; font-weight: bold; cursor: pointer; display: flex; flex-direction: column; align-items: center;
        }
        .btn:active { background: #e7f3ff; border-color: #1877f2; }
        .btn span { font-size: 22px; margin-bottom: 5px; }

        .ai-box { 
            background: #fff; border-right: 4px solid #1877f2; padding: 15px; border-radius: 8px; 
            margin-bottom: 15px; display: none; box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .ai-title { color: #1877f2; font-weight: 900; font-size: 13px; margin-bottom: 5px; }
        .ai-text { font-size: 14px; line-height: 1.5; color: #4b4f56; }

        .card { background: #fff; padding: 15px; margin-bottom: 10px; border-radius: 8px; box-shadow: 0 1px 2px rgba(0,0,0,0.1); }
        .id-text { font-size: 11px; color: #90949c; margin-bottom: 8px; }
        .link-btn { 
            display: block; background: #42b72a; color: #fff; text-decoration: none; 
            text-align: center; padding: 12px; border-radius: 6px; font-weight: bold; 
        }

        .loader { display: none; width: 30px; height: 30px; border: 3px solid #f3f3f3; border-top: 3px solid #1877f2; border-radius: 50%; animation: spin 1s linear infinite; margin: 20px auto; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .status { text-align: center; font-size: 13px; color: #606770; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="header"><h1>🦅 DZ Ad Hunter</h1></div>
    
    <div class="grid">
        <button onclick="scan('home')" class="btn"><span>🏠</span>منزل</button>
        <button onclick="scan('beauty')" class="btn"><span>💄</span>تجميل</button>
        <button onclick="scan('tech')" class="btn"><span>📱</span>تقنية</button>
        <button onclick="scan('kids')" class="btn"><span>👶</span>أطفال</button>
        <button onclick="scan('fashion')" class="btn"><span>👗</span>أزياء</button>
        <button onclick="scan('sports')" class="btn"><span>⚽</span>رياضة</button>
    </div>

    <div class="loader" id="loader"></div>
    <div class="status" id="status"></div>

    <div id="aiBox" class="ai-box">
        <div class="ai-title">✨ نصيحة ذكية للمنتج:</div>
        <div id="aiText" class="ai-text"></div>
    </div>

    <div id="results"></div>

    <script>
        async function scan(niche) {
            const loader = document.getElementById('loader');
            const status = document.getElementById('status');
            const aiBox = document.getElementById('aiBox');
            const results = document.getElementById('results');

            loader.style.display = 'block';
            aiBox.style.display = 'none';
            results.innerHTML = '';
            status.innerText = 'جاري جلب الإعلانات بسرعة...';

            try {
                const res = await fetch(`/get_data?niche=${niche}`);
                const data = await res.json();

                if (data.status === 'success') {
                    status.innerHTML = `✅ الكلمة: <b>${data.keyword}</b>`;
                    
                    // إظهار الذكاء الاصطناعي فقط إذا نجح الرد
                    if (data.ai_tip) {
                        aiBox.style.display = 'block';
                        document.getElementById('aiText').innerText = data.ai_tip;
                    }

                    // عرض الإعلانات
                    data.links.forEach(l => {
                        results.innerHTML += `
                            <div class="card">
                                <div class="id-text">LIBRARY ID: ${l.id}</div>
                                <a href="${l.url}" target="_blank" class="link-btn">🔗 فتح الإعلان</a>
                            </div>`;
                    });
                } else {
                    status.innerText = '❌ لم نجد نتائج، حاول مرة أخرى.';
                }
            } catch (e) {
                status.innerText = '❌ خطأ في السيرفر.';
            } finally {
                loader.style.display = 'none';
            }
        }
    </script>
</body>
</html>
"""

def get_links_stable(keyword):
    """محرك جلب الإعلانات المستقر (خفيف وسريع)"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu', '--single-process'])
        page = browser.new_context().new_page()
        # حظر الميديا لضمان السرعة القصوى
        page.route("**/*", lambda r: r.abort() if r.request.resource_type in ["image", "media", "font", "stylesheet"] else r.continue_())
        
        try:
            page.goto(f"https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=DZ&q={keyword}", timeout=60000)
            page.wait_for_timeout(4000)
            
            raw_ids = page.evaluate("""() => {
                const divs = Array.from(document.querySelectorAll('div'));
                const texts = divs.filter(d => d.innerText.includes('ID:') && d.innerText.length < 100);
                return [...new Set(texts.map(t => t.innerText))].slice(0, 8);
            }""")
            
            links = []
            for t in raw_ids:
                m = re.search(r'ID: (\d+)', t)
                if m: links.append({"id": m.group(1), "url": f"https://www.facebook.com/ads/library/?id={m.group(1)}"})
            return links
        except: return []
        finally: browser.close()

def get_ai_tip_safe(keyword):
    """جلب نصيحة AI بشكل آمن لا يعطل الكود الأساسي"""
    try:
        response = model.generate_content(f"أعطني سطر إعلاني واحد قصير لمنتج: {keyword}")
        return response.text
    except: return None

@app.route('/')
def index(): return render_template_string(HTML_TEMPLATE)

@app.route('/get_data')
def get_data():
    niche = request.args.get('niche', 'home')
    keyword = random.choice(NICHES.get(niche, NICHES['home']))
    
    # 1. جلب الإعلانات أولاً (الأولوية للسرعة)
    links = get_links_stable(keyword)
    
    # 2. جلب AI (إذا فشل لا يهم)
    ai_tip = get_ai_tip_safe(keyword)
    
    if links:
        return jsonify({"status": "success", "keyword": keyword, "links": links, "ai_tip": ai_tip})
    return jsonify({"status": "empty"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
