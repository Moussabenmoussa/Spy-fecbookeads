import os
from flask import Flask, jsonify, request, render_template_string
from playwright.sync_api import sync_playwright
import re
from datetime import datetime
import random

app = Flask(__name__)

# --- قوائم البحث "الجوكر" (Broad Match) ---
# هذه الكلمات موجودة في ملايين الإعلانات، مما يضمن ظهور نتائج دائماً
NICHES = {
    "home": ["Cuisine", "Maison", "Nettoyage", "Décoration", "Outil"],
    "beauty": ["Soins", "Visage", "Cheveux", "Beauté", "Parfum"],
    "tech": ["Montre", "Écouteurs", "Bluetooth", "Chargeur", "Gadget"],
    "kids": ["Jouet", "Bébé", "Enfant", "Éducatif", "Jeu"],
    "fashion": ["Sac", "Chaussures", "Vêtement", "Homme", "Femme"]
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DZ Ad Hunter 🚀</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f4f6f8; margin: 0; padding: 0; }
        .container { max-width: 1000px; margin: 0 auto; padding: 20px; }
        
        /* 1. الهيدر وشريط البحث في الأعلى تماماً */
        .top-section { background: white; padding: 30px; border-radius: 0 0 20px 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); text-align: center; margin-bottom: 30px; }
        .top-section h1 { margin: 0 0 10px 0; color: #1a73e8; }
        .top-section p { color: #666; margin-bottom: 25px; }

        /* شريط البحث اليدوي */
        .search-bar { display: flex; gap: 10px; justify-content: center; max-width: 600px; margin: 0 auto 20px; }
        input { flex: 1; padding: 15px; border: 2px solid #eee; border-radius: 10px; font-size: 16px; outline: none; transition: 0.3s; }
        input:focus { border-color: #1a73e8; }
        .btn-main { background: #1a73e8; color: white; border: none; padding: 15px 30px; border-radius: 10px; cursor: pointer; font-weight: bold; font-size: 16px; }
        .btn-main:hover { background: #1557b0; }

        /* أزرار النيش (التصنيفات) */
        .niche-buttons { display: flex; flex-wrap: wrap; justify-content: center; gap: 10px; margin-top: 15px; }
        .btn-niche { background: #e8f0fe; color: #1a73e8; border: none; padding: 10px 20px; border-radius: 20px; cursor: pointer; font-weight: 600; transition: 0.2s; }
        .btn-niche:hover { background: #d2e3fc; transform: translateY(-2px); }

        /* منطقة النتائج */
        .results-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
        
        .ad-card { background: white; border-radius: 12px; overflow: hidden; border: 1px solid #e0e0e0; transition: transform 0.2s; position: relative; }
        .ad-card:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.08); }
        
        .badge { position: absolute; top: 10px; left: 10px; padding: 5px 10px; border-radius: 15px; color: white; font-size: 11px; font-weight: bold; }
        .badge-winner { background: #34a853; } /* أخضر */
        .badge-test { background: #fbbc04; color: #333; } /* أصفر */

        .ad-body { padding: 20px; }
        .ad-meta { font-size: 12px; color: #888; margin-bottom: 10px; display: flex; justify-content: space-between; }
        .ad-text { font-size: 14px; line-height: 1.6; color: #333; min-height: 60px; }
        
        .loader { display: none; margin: 20px auto; border: 4px solid #f3f3f3; border-top: 4px solid #1a73e8; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .status-msg { text-align: center; color: #555; margin: 20px; font-weight: bold; }
    </style>
</head>
<body>

<div class="top-section">
    <h1>🦅 DZ Ad Hunter</h1>
    <p>محرك البحث الذكي عن المنتجات الرابحة</p>
    
    <div class="search-bar">
        <input type="text" id="keyword" placeholder="بحث عن منتج (مثلاً: ساعة)...">
        <button onclick="startScan('manual')" class="btn-main" id="searchBtn">بحث</button>
    </div>

    <p style="font-size: 14px; color:#999;">أو اختر قسماً للبحث التلقائي:</p>
    
    <div class="niche-buttons">
        <button onclick="startScan('niche', 'home')" class="btn-niche">🏠 المنزل</button>
        <button onclick="startScan('niche', 'beauty')" class="btn-niche">💄 تجميل</button>
        <button onclick="startScan('niche', 'tech')" class="btn-niche">📱 إلكترونيات</button>
        <button onclick="startScan('niche', 'kids')" class="btn-niche">👶 أطفال</button>
        <button onclick="startScan('niche', 'fashion')" class="btn-niche">👗 ملابس</button>
    </div>
</div>

<div class="container">
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
            endpoint = `/discover?niche=${nicheType}`;
            status.innerText = `🤖 جاري البحث في قسم: ${nicheType}...`;
        }

        loader.style.display = "block";
        resultsDiv.innerHTML = "";
        
        try {
            const response = await fetch(endpoint);
            const json = await response.json();

            if (json.status === "success") {
                status.innerHTML = `✅ النتائج: ${json.count} | الكلمة: <b style="color:#1a73e8">${json.keyword || 'مخصص'}</b>`;
                
                json.data.forEach(ad => {
                    let badgeHTML = ad.is_winner 
                        ? `<span class="badge badge-winner">🔥 WINNER (+${ad.days_running} Days)</span>` 
                        : `<span class="badge badge-test">🧪 TEST (${ad.days_running} Days)</span>`;

                    resultsDiv.innerHTML += `
                        <div class="ad-card">
                            ${badgeHTML}
                            <div class="ad-body">
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
            status.innerText = "❌ خطأ في الاتصال بالسيرفر.";
        } finally {
            loader.style.display = "none";
        }
    }
</script>
</body>
</html>
"""

def analyze_ad(raw_text):
    # استخراج البيانات
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
            if days_running >= 4: is_winner = True
        except: pass

    # تنظيف النص
    clean_text = raw_text
    if "Platforms" in raw_text: clean_text = raw_text.split("Platforms")[1]
    
    # إزالة الكلمات الزائدة
    for noise in ["Open Dropdown", "See ad details", "Sponsored", "Active", "Library ID"]:
        clean_text = clean_text.replace(noise, "")
        
    clean_text = clean_text[:120] + "..."

    return {
        "id": ad_id, "start_date": start_date_str, "days_running": days_running,
        "is_winner": is_winner, "clean_text": clean_text.strip()
    }

def core_hunter(keyword):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()
        try:
            url = f"https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=DZ&q={keyword}"
            
            # 1. زيادة وقت الانتظار (هام جداً للسيرفر المجاني)
            page.goto(url, timeout=90000) 
            page.wait_for_timeout(8000) # انتظار 8 ثواني كاملة للتحميل
            
            # 2. مصفاة واسعة جداً (Broad Selector)
            # بدلاً من البحث عن نص محدد قد يتغير، نبحث عن أي كارت إعلان
            raw_ads = page.evaluate("""() => {
                const divs = Array.from(document.querySelectorAll('div'));
                
                // نبحث عن أي ديف يحتوي على كلمة ID ورقم، أو كلمة Started running
                // هذا يضمن التقاط الإعلان سواء كان بالإنجليزية أو غيرها
                const cards = divs.filter(d => 
                    (d.innerText.includes('Library ID') || d.innerText.includes('Started running')) 
                    && d.innerText.length > 40 
                    && d.innerText.length < 800
                );
                
                // إزالة التكرار
                return [...new Set(cards.map(c => c.innerText))].slice(0, 8);
            }""")
            
            if len(raw_ads) == 0: return None
            
            analyzed = [analyze_ad(raw) for raw in raw_ads]
            # ترتيب النتائج: الرابح أولاً
            analyzed.sort(key=lambda x: x['days_running'], reverse=True)
            return analyzed
        except Exception as e:
            print(f"Error: {e}")
            return None
        finally: browser.close()

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/scan', methods=['GET'])
def scan_endpoint():
    query = request.args.get('q', 'Livraison')
    results = core_hunter(query)
    if results:
        return jsonify({"status": "success", "count": len(results), "keyword": query, "data": results})
    return jsonify({"status": "empty", "msg": "الصفحة ثقيلة ولم تفتح في الوقت المحدد، حاول مرة أخرى."})

@app.route('/discover', methods=['GET'])
def discover_endpoint():
    niche_type = request.args.get('niche', 'home')
    # اختيار كلمة مضمونة من القائمة
    keywords_list = NICHES.get(niche_type, NICHES['home'])
    random_keyword = random.choice(keywords_list)
    
    results = core_hunter(random_keyword)
    
    if results:
        return jsonify({
            "status": "success", 
            "count": len(results), 
            "keyword": random_keyword,
            "data": results
        })
    
    return jsonify({"status": "empty", "msg": f"حاول مرة أخرى (بحثنا عن '{random_keyword}' ولم نلتقط شيئاً)."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
