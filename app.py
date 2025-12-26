import os
from flask import Flask, jsonify, request, render_template_string
from playwright.sync_api import sync_playwright
import re

app = Flask(__name__)

# --- واجهة العرض الاحترافية (Dashboard) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DZ Ad Hunter - النتائج 🦅</title>
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
        
        /* تصميم بطاقة الإعلان */
        .ad-card { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.08); transition: transform 0.2s; border: 1px solid #ddd; }
        .ad-card:hover { transform: translateY(-5px); box-shadow: 0 8px 16px rgba(0,0,0,0.12); }
        
        .ad-header { padding: 15px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; }
        .status-badge { background: #e7f3ff; color: #1877f2; padding: 5px 10px; border-radius: 15px; font-size: 12px; font-weight: bold; }
        
        .ad-body { padding: 15px; }
        .ad-info { font-size: 13px; color: #65676b; margin-bottom: 10px; }
        .ad-text { font-size: 15px; color: #1c1e21; line-height: 1.5; min-height: 60px; }
        
        .ad-footer { padding: 15px; background: #f7f8fa; text-align: center; border-top: 1px solid #eee; }
        .view-btn { text-decoration: none; color: #1877f2; font-weight: bold; font-size: 14px; }

        .loader { display: none; margin: 20px auto; border: 4px solid #f3f3f3; border-top: 4px solid #1877f2; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>

<div class="container">
    <div class="header">
        <h1>🦅 DZ Ad Hunter <span style="color:#1877f2">Pro</span></h1>
        <p>تجسس على المنافسين واكتشف المنتجات الرابحة</p>
    </div>

    <div class="search-area">
        <input type="text" id="keyword" placeholder="ابحث عن منتج (مثلاً: ساعة، توصيل)...">
        <button onclick="startScan()" id="searchBtn">بحث</button>
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
        status.innerText = "جاري الاتصال بفيسبوك وسحب البيانات... (انتظر 40 ثانية)";

        try {
            const response = await fetch(`/scan?q=${keyword}`);
            const json = await response.json();

            if (json.status === "success") {
                status.innerText = `✅ تم العثور على ${json.count} إعلانات نشطة!`;
                
                json.data.forEach(ad => {
                    resultsDiv.innerHTML += `
                        <div class="ad-card">
                            <div class="ad-header">
                                <span class="status-badge">🟢 Active</span>
                                <small style="color:#888">ID: ${ad.id}</small>
                            </div>
                            <div class="ad-body">
                                <div class="ad-info">📅 بدأ في: ${ad.start_date}</div>
                                <p class="ad-text">${ad.clean_text}</p>
                            </div>
                            <div class="ad-footer">
                                <a href="#" class="view-btn">🔗 تفاصيل الإعلان</a>
                            </div>
                        </div>
                    `;
                });
            } else {
                status.innerText = `⚠️ ${json.msg}`;
            }
        } catch (err) {
            status.innerText = "❌ حدث خطأ في الاتصال بالسيرفر.";
        } finally {
            btn.disabled = false;
            loader.style.display = "none";
        }
    }
</script>
</body>
</html>
"""

def clean_ad_data(raw_text):
    """
    وظيفة لتنظيف النص الخام واستخراج المعلومات المهمة
    """
    # 1. استخراج رقم المعرف (ID)
    id_match = re.search(r'ID: (\d+)', raw_text)
    ad_id = id_match.group(1) if id_match else "غير متوفر"

    # 2. استخراج التاريخ
    date_match = re.search(r'Started running on (.*?) Platforms', raw_text)
    start_date = date_match.group(1) if date_match else "غير محدد"

    # 3. تنظيف النص (إزالة الكلمات التقنية)
    # نزيل كل ما هو قبل التاريخ، ونزيل كلمات مثل Open Dropdown
    clean_text = raw_text
    if date_match:
        # نأخذ ما بعد التاريخ
        clean_text = raw_text.split("Platforms")[1] if "Platforms" in raw_text else raw_text
    
    # تنظيف إضافي للكلمات المزعجة
    clean_text = clean_text.replace("Open Dropdown", "").replace("See ad details", "").replace("Sponsored", "")
    clean_text = clean_text[:150] + "..." # تقصير النص

    return {
        "id": ad_id,
        "start_date": start_date,
        "clean_text": clean_text.strip()
    }

def hunt_human_mode(keyword):
    print(f"🚀 بدء البحث عن: {keyword}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
        context = browser.new_context(viewport={'width': 1366, 'height': 768})
        page = context.new_page()

        try:
            url = f"https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=DZ&q={keyword}"
            page.goto(url, timeout=60000)
            page.wait_for_timeout(5000)

            # استخراج النصوص الخام
            raw_ads = page.evaluate("""() => {
                const divs = Array.from(document.querySelectorAll('div'));
                // نبحث عن الحاويات التي فيها ID لأنها الأضمن
                const cards = divs.filter(d => d.innerText.includes('Library ID:') && d.innerText.length > 50 && d.innerText.length < 800);
                const uniqueTexts = [...new Set(cards.map(c => c.innerText))];
                return uniqueTexts.slice(0, 6); // أول 6 نتائج
            }""")

            if len(raw_ads) == 0:
                return {"status": "empty", "msg": "لم يتم العثور على نتائج نصية."}

            # تنظيف البيانات في بايثون
            cleaned_results = []
            for raw in raw_ads:
                cleaned_results.append(clean_ad_data(raw))

            return {"status": "success", "count": len(cleaned_results), "data": cleaned_results}

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
    return jsonify(hunt_human_mode(query))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
