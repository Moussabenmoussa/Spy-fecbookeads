
import os, re, random
import google.generativeai as genai
from flask import Flask, jsonify, request, render_template_string
from playwright.sync_api import sync_playwright

app = Flask(__name__)

# --- إعدادات Gemini AI (النسخة الاقتصادية) ---
os.environ["GEMINI_API_KEY"] = "AIzaSyDV8pA6K4mFs0vnRwjtEKEdTJyJkUby9IU"
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# استخدام موديل 'flash' لأنه أسرع وأفضل للحسابات المجانية
model = genai.GenerativeModel('gemini-1.5-flash')

# قوائم الكلمات
NICHES = {
    "home": ["Cuisine", "Maison", "Nettoyage", "Décoration", "Outil", "Ustensiles"],
    "beauty": ["Soins", "Visage", "Cheveux", "Beauté", "Parfum", "Makeup"],
    "tech": ["Montre", "Écouteurs", "Bluetooth", "Chargeur", "Gadget", "Smartwatch"],
    "kids": ["Jouet", "Bébé", "Enfant", "Éducatif", "Jeu", "Puzzle"],
    "fashion": ["Sac", "Chaussures", "Vêtement", "Homme", "Femme", "Mode"],
    "sports": ["Sport", "Fitness", "Gym", "Équipement", "Running", "Basket"]
}

# --- واجهة الموبايل الجميلة (نفس التصميم) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>DZ Ad Hunter Mobile 📱</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
        :root { --primary: #2563eb; --bg: #f8fafc; --card: #ffffff; }
        * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
        
        body { font-family: 'Cairo', sans-serif; background: var(--bg); margin: 0; padding: 15px; color: #334155; }
        .container { max-width: 600px; margin: 0 auto; padding-bottom: 50px; }
        h1 { text-align: center; color: #1e293b; font-size: 22px; margin-bottom: 5px; }
        p { text-align: center; color: #64748b; font-size: 14px; margin-top: 0; }

        .grid-buttons { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 20px; }
        .btn-main { background: white; border: 2px solid #e2e8f0; border-radius: 12px; padding: 15px; font-size: 16px; font-weight: 700; color: #334155; cursor: pointer; transition: 0.2s; display: flex; flex-direction: column; align-items: center; }
        .btn-main span { font-size: 24px; margin-bottom: 5px; }
        .btn-main:active { transform: scale(0.96); background: #eff6ff; border-color: var(--primary); color: var(--primary); }

        .ai-card { background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%); color: white; padding: 20px; border-radius: 16px; margin-bottom: 20px; display: none; box-shadow: 0 10px 20px rgba(37, 99, 235, 0.2); }
        .ai-title { font-weight: 800; font-size: 14px; opacity: 0.9; margin-bottom: 10px; display: flex; align-items: center; gap: 5px; }
        .ai-text { font-size: 15px; line-height: 1.6; white-space: pre-wrap; }

        .card { background: var(--card); padding: 15px; margin-bottom: 15px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); display: flex; flex-direction: column; gap: 10px; }
        .id-badge { background: #f1f5f9; color: #64748b; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: bold; width: fit-content; }
        .link-btn { text-decoration: none; background: #22c55e; color: white; padding: 12px; border-radius: 8px; font-weight: bold; text-align: center; display: block; width: 100%; }
        
        .loader { display: none; width: 40px; height: 40px; margin: 20px auto; border: 4px solid #e2e8f0; border-top: 4px solid var(--primary); border-radius: 50%; animation: spin 1s linear infinite; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .status { text-align: center; color: #64748b; font-weight: 600; margin-top: 10px; font-size: 14px; }
    </style>
</head>
<body>

<div class="container">
    <h1>🦅 DZ Ad Hunter</h1>
    <p>نظام القنص الذكي (نسخة الموبايل)</p>
    
    <div class="grid-buttons">
        <button onclick="scan('home')" class="btn-main"><span>🏠</span>منزل</button>
        <button onclick="scan('beauty')" class="btn-main"><span>💄</span>تجميل</button>
        <button onclick="scan('tech')" class="btn-main"><span>📱</span>تقنية</button>
        <button onclick="scan('kids')" class="btn-main"><span>👶</span>أطفال</button>
        <button onclick="scan('fashion')" class="btn-main"><span>👗</span>أزياء</button>
        <button onclick="scan('sports')" class="btn-main"><span>⚽</span>رياضة</button>
    </div>

    <div class="loader" id="loader"></div>
    <div class="status" id="status"></div>

    <div id="aiResult" class="ai-card">
        <div class="ai-title">✨ نصيحة Gemini الذكية:</div>
        <div id="aiText" class="ai-text"></div>
    </div>

    <div id="results"></div>
</div>

<script>
async function scan(n){
    const loader = document.getElementById('loader');
    const resultsDiv = document.getElementById('results');
    const status = document.getElementById('status');
    const aiCard = document.getElementById('aiResult');
    
    loader.style.display = 'block';
    resultsDiv.innerHTML = '';
    aiCard.style.display = 'none';
    status.innerText = `جاري الاتصال بـ Gemini والبحث في ${n}...`;
    
    const btns = document.querySelectorAll('button');
    btns.forEach(b => b.disabled = true);

    try {
        const res = await fetch(`/get_links?niche=${n}`);
        const data = await res.json();
        
        if(data.status === 'success'){
            status.innerHTML = `✅ تم! الكلمة: <b style="color:#2563eb">${data.keyword}</b> | النتائج: ${data.count}`;
            
            if(data.ai_tip) {
                aiCard.style.display = 'block';
                document.getElementById('aiText').innerText = data.ai_tip;
            }

            data.links.forEach(link => {
                resultsDiv.innerHTML += `
                <div class="card">
                    <div class="id-badge">ID: ${link.id}</div>
                    <a href="${link.url}" target="_blank" class="link-btn">🔗 فتح الإعلان في فيسبوك</a>
                </div>`;
            });
        } else {
            status.innerText = "⚠️ لم يتم العثور على نتائج، حاول مرة أخرى.";
        }
    } catch(e) {
        status.innerText = "❌ حدث خطأ في الاتصال";
    } finally {
        loader.style.display = 'none';
        btns.forEach(b => b.disabled = false);
    }
}
</script>
</body>
</html>
"""

# --- وظيفة الذكاء الاصطناعي (محسنة للمجاني) ---
def get_ai_tip(keyword):
    try:
        # نص طلب بسيط جداً لتقليل استهلاك التوكنز
        prompt = f"أكتب جملة إعلانية واحدة قصيرة جداً ومشوقة بالدارجة الجزائرية لمنتج: {keyword}."
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # في حالة انتهاء الرصيد المجاني، لا نوقف التطبيق
        print(f"AI Error: {e}") 
        return "" 

# --- وظيفة السكرابينج (الكود الأصلي الموثوق) ---
def get_direct_links(keyword):
    with sync_playwright() as p:
        b = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu', '--single-process']
        )
        page = b.new_context().new_page()
        page.route("**/*", lambda r: r.abort() if r.request.resource_type in ["image", "media", "font", "stylesheet"] else r.continue_())

        try:
            page.goto(f"https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=DZ&q={keyword}", timeout=60000)
            page.wait_for_timeout(4000)

            raw_ids = page.evaluate("""() => {
                const divs = Array.from(document.querySelectorAll('div'));
                const idTexts = divs.filter(d => d.innerText.includes('ID:') && d.innerText.length < 100);
                return [...new Set(idTexts.map(c => c.innerText))].slice(0, 8);
            }""")

            links = []
            for text in raw_ids:
                match = re.search(r'ID: (\d+)', text)
                if match:
                    ad_id = match.group(1)
                    links.append({"id": ad_id, "url": f"https://www.facebook.com/ads/library/?id={ad_id}"})
            return links
        except: return []
        finally: b.close()

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/get_links')
def get_links():
    niche = request.args.get('niche', 'home')
    keyword_list = NICHES.get(niche, NICHES['home'])
    keyword = random.choice(keyword_list)
    
    # محاولة جلب الذكاء الاصطناعي (لن توقف التطبيق إذا فشلت)
    ai_advice = get_ai_tip(keyword)
    
    # جلب الروابط
    links = get_direct_links(keyword)
    
    if links:
        return jsonify({
            "status": "success", 
            "count": len(links), 
            "keyword": keyword, 
            "links": links,
            "ai_tip": ai_advice
        })
    return jsonify({"status": "empty"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
