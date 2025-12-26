import os
from flask import Flask, jsonify, request, render_template_string
from playwright.sync_api import sync_playwright
import re
from datetime import datetime
import random

app = Flask(__name__)

# --- القواميس الذكية (Smart Dictionaries) ---
# بدلاً من قائمة واحدة، لدينا قوائم متخصصة
NICHES = {
    "home": [
        "Cuisine", "Mixeur", "Hachoir", "Organisateur", "Salle de bain", 
        "Nettoyage", "Mop", "Décoration", "Lampe", "Outil"
    ],
    "beauty": [
        "Soins visage", "Anti rides", "Cheveux", "Lisseur", "Épilateur", 
        "Maquillage", "Parfum", "Blanchiment", "Massager"
    ],
    "tech": [
        "Smart watch", "Écouteurs", "Bluetooth", "Support voiture", "Chargeur", 
        "Caméra", "Projecteur", "Gadget", "Power bank"
    ],
    "kids": [
        "Jouet", "Bébé", "Éducatif", "Enfant", "Peluche", 
        "Cartable", "Tablette enfant", "Puzzle"
    ],
    "fashion": [
        "Sac", "Chaussures", "Montre homme", "Vêtement", "Hijab", 
        "Ensemble", "Pyjama", "Orthopédique"
    ]
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DZ Ad Hunter - Niches 🎯</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f8f9fa; margin: 0; padding: 20px; }
        .container { max-width: 1100px; margin: 0 auto; }
        
        .header { text-align: center; margin-bottom: 40px; }
        .header h1 { color: #2c3e50; font-weight: 800; font-size: 2.5rem; }
        .header p { color: #7f8c8d; font-size: 1.1rem; }
        
        /* شبكة التصنيفات */
        .niche-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-bottom: 40px; }
        
        .niche-btn {
            background: white; border: none; padding: 20px; border-radius: 15px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05); cursor: pointer; transition: all 0.3s ease;
            display: flex; flex-direction: column; align-items: center; gap: 10px;
        }
        .niche-btn:hover { transform: translateY(-5px); box-shadow: 0 8px 20px rgba(0,0,0,0.1); }
        .niche-btn:active { transform: scale(0.95); }
        
        .icon { font-size: 2rem; }
        .label { font-weight: bold; color: #34495e; }
        
        /* البحث اليدوي */
        .manual-search { background: white; padding: 15px; border-radius: 50px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); display: flex; max-width: 600px; margin: 0 auto 40px; }
        input { flex: 1; border: none; padding: 10px 20px; font-size: 16px; outline: none; border-radius: 50px; }
        .search-btn { background: #3498db; color: white; border: none; padding: 10px 30px; border-radius: 50px; cursor: pointer; font-weight: bold; }
        
        /* النتائج */
        .results-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 25px; }
        
        .ad-card { background: white; border-radius: 15px; overflow: hidden; box-shadow: 0 5px 15px rgba(0,0,0,0.08); position: relative; transition: transform 0.2s; }
        .ad-card:hover { transform: translateY(-5px); }
        
        .badge { position: absolute; top: 15px; left: 15px; padding: 6px 12px; border-radius: 20px; color: white; font-weight: bold; font-size: 11px; z-index: 2; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }
        .badge-winner { background: #2ecc71; }
        .badge-test { background: #f1c40f; color: #333; }
        
        .ad-content { padding: 20px; }
        .ad-meta { display: flex; justify-content: space-between; font-size: 12px; color: #95a5a6; margin-bottom: 10px; }
        .ad-text { color: #2c3e50; line-height: 1.6; font-size: 14px; min-height: 80px; }
        
        .loader { display: none; margin: 20px auto; border: 4px solid #f3f3f3; border-top: 4px solid #3498db; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        
        .status-msg { text-align: center; font-weight: bold; color: #7f8c8d; margin-top: 20px; }
    </style>
</head>
<body>

<div class="container">
    <div class="header">
        <h1>🦅 DZ Ad Hunter</h1>
        <p>اختر المجال الذي تريد العمل فيه، وسنجد لك المنتج الرابح</p>
    </div>

    <div class="niche-grid">
        <button onclick="startScan('niche', 'home')" class="niche-btn">
            <span class="icon">🏠</span>
            <span class="label">المنزل والمطبخ</span>
        </button>
        <button onclick="startScan('niche', 'beauty')" class="niche-btn">
            <span class="icon">💄</span>
            <span class="label">الجمال والعناية</span>
        </button>
        <button onclick="startScan('niche', 'tech')" class="niche-btn">
            <span class="icon">📱</span>
            <span class="label">إلكترونيات</span>
        </button>
        <button onclick="startScan('niche', 'kids')" class="niche-btn">
            <span class="icon">👶</span>
            <span class="label">أطفال وألعاب</span>
        </button>
        <button onclick="startScan('niche', 'fashion')" class="niche-btn">
            <span class="icon">👗</span>
            <span class="label">أزياء وموضة</span>
        </button>
    </div>

    <div class="manual-search">
        <input type="text" id="keyword" placeholder="أو ابحث عن منتج محدد...">
        <button onclick="startScan('manual')" class="search-btn">بحث</button>
    </div>

    <div class="loader" id="loader"></div>
    <div id="statusMsg" class="status-msg"></div>

    <div class="results-grid" id="results"></div>
</div>

<script>
    async function startScan(mode, nicheType='') {
        const loader = document.getElementById('loader');
        const resultsDiv = document.getElementById('results');
        const status = document.getElementById('statusMsg');
        
        let endpoint = "";
        
        if (mode === 'manual') {
            const val = document.getElementById('keyword').value;
            if (!val) return;
            endpoint = `/scan?q=${val}`;
            status.innerText = `🔎 جاري البحث عن: ${val}...`;
        } else {
            // بحث حسب النيش
            endpoint = `/discover?niche=${nicheType}`;
            status.innerText = `🤖 الروبوت يبحث عن منتجات رابحة في قسم: ${nicheType}...`;
        }

        // تعطيل الأزرار مؤقتاً (اختياري)
        loader.style.display = "block";
        resultsDiv.innerHTML = "";
        
        try {
            const response = await fetch(endpoint);
            const json = await response.json();

            if (json.status === "success") {
                if (mode === 'manual') {
                    status.innerText = `✅ النتائج: ${json.count}`;
                } else {
                    status.innerHTML = `✅ الكلمة المختارة: <b style="color:#e67e22">${json.keyword}</b> | النتائج: ${json.count}`;
                }

                json.data.forEach(ad => {
                    let badgeHTML = ad.is_winner 
                        ? `<span class="badge badge-winner">🔥 WINNER (+${ad.days_running} Days)</span>` 
                        : `<span class="badge badge-test">🧪 TEST (${ad.days_running} Days)</span>`;

                    resultsDiv.innerHTML += `
                        <div class="ad-card">
                            ${badgeHTML}
                            <div class="ad-content">
                                <div class="ad-meta">
                                    <span>📅 ${ad.start_date}</span>
                                    <span>ID: ${ad.id}</span>
                                </div>
                                <p class="ad-text">${ad.clean_text}</p>
                            </div>
                        </div>
                    `;
                });
            } else {
                status.innerText = `⚠️ ${json.msg}`;
            }
        } catch (err) {
            status.innerText = "❌ خطأ في الاتصال";
        } finally {
            loader.style.display = "none";
        }
    }
</script>
</body>
</html>
"""

def analyze_ad(raw_text):
    # دالة التحليل
    id_match = re.search(r'ID: (\d+)', raw_text)
    ad_id = id_match.group(1) if id_match else "N/A"
    
    date_match = re.search(r'Started running on (.*?) Platforms', raw_text)
    start_date_str = date_match.group(1).strip() if date_match else ""
    
    days_running = 0
    is_winner = False
    
    if start_date_str:
        try:
            ad_date = datetime.strptime(start_date_str, "%b %d, %Y")
            days_running = (datetime.now() - ad_date).days
            if days_running >= 5: is_winner = True
        except: pass

    clean_text = raw_text
    if "Platforms" in raw_text: clean_text = raw_text.split("Platforms")[1]
    clean_text = clean_text.replace("Open Dropdown", "").replace("Sponsored", "")[:120] + "..."

    return {
        "id": ad_id, "start_date": start_date_str, "days_running": days_running,
        "is_winner": is_winner, "clean_text": clean_text.strip()
    }

def core_hunter(keyword):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
        context = browser.new_context(viewport={'width': 1366, 'height': 768})
        page = context.new_page()
        try:
            url = f"https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=DZ&q={keyword}"
            page.goto(url, timeout=60000)
            page.wait_for_timeout(5000)
            
            raw_ads = page.evaluate("""() => {
                const divs = Array.from(document.querySelectorAll('div'));
                const cards = divs.filter(d => d.innerText.includes('Library ID:') && d.innerText.length > 50 && d.innerText.length < 800);
                return [...new Set(cards.map(c => c.innerText))].slice(0, 8);
            }""")
            
            if len(raw_ads) == 0: return None
            
            analyzed = [analyze_ad(raw) for raw in raw_ads]
            analyzed.sort(key=lambda x: x['days_running'], reverse=True)
            return analyzed
        except: return None
        finally: browser.close()

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/scan', methods=['GET'])
def scan_endpoint():
    query = request.args.get('q', 'Livraison')
    results = core_hunter(query)
    if results:
        return jsonify({"status": "success", "count": len(results), "data": results})
    return jsonify({"status": "empty", "msg": "لم يتم العثور على نتائج."})

@app.route('/discover', methods=['GET'])
def discover_endpoint():
    # استقبال نوع النيش من الزر
    niche_type = request.args.get('niche', 'home')
    
    # اختيار كلمة عشوائية من النيش المحدد فقط
    # إذا لم يكن النيش موجوداً نستخدم المنزل كافتراضي
    keywords_list = NICHES.get(niche_type, NICHES['home'])
    random_keyword = random.choice(keywords_list)
    
    print(f"🎯 Niche: {niche_type} | Keyword: {random_keyword}")
    
    results = core_hunter(random_keyword)
    
    if results:
        return jsonify({
            "status": "success", 
            "count": len(results), 
            "keyword": random_keyword,
            "data": results
        })
    
    return jsonify({"status": "empty", "msg": f"جرب مرة أخرى (بحثنا عن '{random_keyword}')."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
