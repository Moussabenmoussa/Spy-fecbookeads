import os
from flask import Flask, jsonify, request, render_template_string
from playwright.sync_api import sync_playwright
import re
from datetime import datetime

app = Flask(__name__)

# --- واجهة العرض الذكية ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DZ Ad Hunter - Sniper Mode 🎯</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f0f2f5; margin: 0; padding: 20px; }
        .container { max-width: 1000px; margin: 0 auto; }
        
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { color: #1c1e21; font-weight: 800; }
        
        .search-area { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); display: flex; gap: 10px; justify-content: center; }
        input { padding: 15px; width: 60%; border: 1px solid #ccc; border-radius: 8px; font-size: 16px; }
        button { padding: 15px 30px; background: #1877f2; color: white; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 16px; }
        button:hover { background: #155db5; }
        button:disabled { background: #ccc; }

        .results-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; margin-top: 30px; }
        
        .ad-card { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.08); transition: transform 0.2s; border: 1px solid #ddd; position: relative; }
        .ad-card:hover { transform: translateY(-5px); }
        
        .badge { position: absolute; top: 10px; left: 10px; padding: 5px 10px; border-radius: 20px; color: white; font-weight: bold; font-size: 12px; z-index: 10; }
        .badge-winner { background: #2ecc71; box-shadow: 0 2px 5px rgba(46, 204, 113, 0.4); } /* أخضر للرابح */
        .badge-test { background: #f1c40f; color: #333; } /* أصفر للاختبار */
        
        .ad-body { padding: 15px; margin-top: 20px; }
        .ad-date { font-size: 12px; color: #888; margin-bottom: 5px; display: block; }
        .ad-text { font-size: 14px; color: #1c1e21; line-height: 1.5; }
        
        .loader { display: none; margin: 20px auto; border: 4px solid #f3f3f3; border-top: 4px solid #1877f2; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>

<div class="container">
    <div class="header">
        <h1>🦅 DZ Ad Hunter <span style="color:#1877f2">Sniper</span></h1>
        <p>ابحث عن المنتجات التي صمدت في السوق (الرابحة فقط)</p>
    </div>

    <div class="search-area">
        <input type="text" id="keyword" placeholder="ابحث عن منتج (مثلاً: ساعة، توصيل)...">
        <button onclick="startScan()" id="searchBtn">قنص</button>
    </div>

    <div class="loader" id="loader"></div>
    <div id="statusMsg" style="text-align: center; margin: 20px; font-weight: bold; color: #555;"></div>

    <div class="results-grid" id="results"></div>
</div>

<script>
    async function startScan() {
        const keyword = document.getElementById('keyword').value;
        const btn = document.getElementById('searchBtn');
        const loader = document.getElementById('loader');
        const resultsDiv = document.getElementById('results');
        const status = document.getElementById('statusMsg');

        if (!keyword) return;

        btn.disabled = true;
        loader.style.display = "block";
        resultsDiv.innerHTML = "";
        status.innerText = "جاري تحليل عمر الإعلانات... (انتظر 40 ثانية)";

        try {
            const response = await fetch(`/scan?q=${keyword}`);
            const json = await response.json();

            if (json.status === "success") {
                status.innerText = `✅ تم العثور على ${json.count} إعلانات!`;
                
                json.data.forEach(ad => {
                    // تحديد البادج بناء على التحليل
                    let badgeHTML = '';
                    if (ad.is_winner) {
                        badgeHTML = `<span class="badge badge-winner">🔥 WINNER (+${ad.days_running} Days)</span>`;
                    } else {
                        badgeHTML = `<span class="badge badge-test">🧪 TEST (${ad.days_running} Days)</span>`;
                    }

                    resultsDiv.innerHTML += `
                        <div class="ad-card">
                            ${badgeHTML}
                            <div class="ad-body">
                                <span class="ad-date">📅 بدأ: ${ad.start_date}</span>
                                <small style="color:#aaa">ID: ${ad.id}</small>
                                <p class="ad-text">${ad.clean_text}</p>
                            </div>
                        </div>
                    `;
                });
            } else {
                status.innerText = `⚠️ ${json.msg}`;
            }
        } catch (err) {
            status.innerText = "❌ حدث خطأ في الاتصال.";
        } finally {
            btn.disabled = false;
            loader.style.display = "none";
        }
    }
</script>
</body>
</html>
"""

def analyze_ad(raw_text):
    """
    تحليل الإعلان: استخراج التاريخ وحساب الأيام لتحديد الرابح
    """
    # 1. استخراج المعرف
    id_match = re.search(r'ID: (\d+)', raw_text)
    ad_id = id_match.group(1) if id_match else "N/A"

    # 2. استخراج التاريخ (Started running on X)
    # الصيغة عادة تكون: Started running on Dec 24, 2025
    date_match = re.search(r'Started running on (.*?) Platforms', raw_text)
    start_date_str = date_match.group(1).strip() if date_match else ""
    
    days_running = 0
    is_winner = False

    # 3. حساب الأيام (المنطق الذكي)
    if start_date_str:
        try:
            # محاولة تحويل النص إلى تاريخ
            # قد تحتاج لتعديل الصيغة حسب لغة السيرفر، هنا نفترض الإنجليزية
            ad_date = datetime.strptime(start_date_str, "%b %d, %Y")
            current_date = datetime.now()
            days_running = (current_date - ad_date).days
            
            # قاعدة الفوز: إذا كان يعمل لأكثر من 5 أيام فهو رابح
            if days_running >= 5:
                is_winner = True
        except:
            days_running = 0 # فشل في حساب التاريخ (يبقى جديد)

    # 4. تنظيف النص
    clean_text = raw_text
    if "Platforms" in raw_text:
        clean_text = raw_text.split("Platforms")[1]
    
    clean_text = clean_text.replace("Open Dropdown", "").replace("See ad details", "").replace("Sponsored", "")
    clean_text = clean_text[:120] + "..."

    return {
        "id": ad_id,
        "start_date": start_date_str,
        "days_running": days_running,
        "is_winner": is_winner,
        "clean_text": clean_text.strip()
    }

def hunt_sniper_mode(keyword):
    print(f"🎯 قنص الإعلانات الرابحة: {keyword}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
        context = browser.new_context(viewport={'width': 1366, 'height': 768})
        page = context.new_page()

        try:
            url = f"https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=DZ&q={keyword}"
            page.goto(url, timeout=60000)
            page.wait_for_timeout(5000)

            # استخراج النصوص
            raw_ads = page.evaluate("""() => {
                const divs = Array.from(document.querySelectorAll('div'));
                const cards = divs.filter(d => d.innerText.includes('Library ID:') && d.innerText.length > 50 && d.innerText.length < 800);
                const uniqueTexts = [...new Set(cards.map(c => c.innerText))];
                return uniqueTexts.slice(0, 8); // نأخذ 8 نتائج
            }""")

            if len(raw_ads) == 0:
                return {"status": "empty", "msg": "لم يتم العثور على إعلانات نصية."}

            # تحليل البيانات في بايثون
            analyzed_results = []
            for raw in raw_ads:
                analyzed_results.append(analyze_ad(raw))

            # ترتيب النتائج: الرابحون أولاً
            analyzed_results.sort(key=lambda x: x['days_running'], reverse=True)

            return {"status": "success", "count": len(analyzed_results), "data": analyzed_results}

        except Exception as e:
            return {"status": "error", "msg": str(e)}
        finally:
            browser.close()

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/scan', methods=['GET'])
def scan_endpoint():
    query = request.args.get('q', 'Livraison')
    return jsonify(hunt_sniper_mode(query))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
