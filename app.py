import os
from flask import Flask, jsonify, request, render_template_string
from pymongo import MongoClient
from playwright.sync_api import sync_playwright
import datetime

app = Flask(__name__)

# --- واجهة الاستخدام ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DZ Ad Hunter - Human Mode 🧠</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #f0f2f5; padding: 20px; text-align: center; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        h1 { color: #1877f2; margin-bottom: 20px; }
        input { padding: 12px; width: 70%; border: 1px solid #ddd; border-radius: 6px; font-size: 16px; }
        button { padding: 12px 25px; background: #1877f2; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 16px; font-weight: bold; }
        button:hover { background: #166fe5; }
        .card { text-align: right; background: #fff; padding: 15px; margin: 15px 0; border: 1px solid #ddd; border-radius: 8px; border-right: 4px solid #42b72a; }
        .status { margin-top: 20px; color: #555; font-weight: bold; }
        .loader { display: none; margin: 20px auto; border: 4px solid #f3f3f3; border-top: 4px solid #1877f2; border-radius: 50%; width: 30px; height: 30px; animation: spin 1s linear infinite; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>
<div class="container">
    <h1>🦅 صياد الإعلانات (المحاكي البشري)</h1>
    <p>هذا الوضع يجبر فيسبوك على إظهار النتائج</p>
    
    <div>
        <input type="text" id="keyword" placeholder="اكتب كلمة البحث (مثلاً: ساعة)...">
        <button onclick="startScan()" id="btn">بحث الآن</button>
    </div>

    <div class="loader" id="loader"></div>
    <p class="status" id="statusMsg"></p>
    <div id="results"></div>
</div>

<script>
    async function startScan() {
        const keyword = document.getElementById('keyword').value;
        const btn = document.getElementById('btn');
        const loader = document.getElementById('loader');
        const status = document.getElementById('statusMsg');
        const resDiv = document.getElementById('results');

        if (!keyword) return;

        btn.disabled = true;
        loader.style.display = "block";
        resDiv.innerHTML = "";
        status.innerText = "جاري فتح فيسبوك والضغط على الأزرار... (انتظر 40 ثانية)";

        try {
            const response = await fetch(`/scan?q=${keyword}`);
            const json = await response.json();

            if (json.status === "success") {
                status.innerText = `✅ تم! وجدنا ${json.count} إعلانات.`;
                json.data.forEach(ad => {
                    resDiv.innerHTML += `
                        <div class="card">
                            <p>${ad}</p>
                        </div>
                    `;
                });
            } else {
                status.innerText = `⚠️ ${json.msg || 'خطأ غير معروف'}`;
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

def hunt_human_mode(keyword):
    print(f"🧠 تشغيل المحاكي البشري للبحث عن: {keyword}")
    
    with sync_playwright() as p:
        # إعدادات المتصفح
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        )
        # حجم شاشة كبير لضمان ظهور الأزرار
        context = browser.new_context(viewport={'width': 1366, 'height': 768})
        page = context.new_page()

        try:
            # 1. الذهاب للرابط المباشر (لكن سننتظر التحميل بذكاء)
            # نستخدم رابط الجزائر وتفعيل كل الإعلانات مباشرة
            url = f"https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=DZ&q={keyword}"
            page.goto(url, timeout=60000)
            
            # 2. الانتظار الذكي (ننتظر اختفاء مؤشر التحميل الخاص بفيسبوك)
            # فيسبوك لديه دائرة تحميل، ننتظر حتى تختفي
            page.wait_for_timeout(5000) 

            # 3. محاولة الضغط على زر "بحث" إذا لزم الأمر أو إعادة كتابة الكلمة
            # أحياناً الرابط لا يكتب الكلمة في المربع، سنتأكد
            
            # نتحقق هل ظهرت نتائج؟ (نبحث عن كروت الإعلانات)
            # كروت الإعلانات عادة تكون داخل Divs ولها كلاسات عشوائية، لكن تحتوي دائماً على كلمة "ID:"
            try:
                page.wait_for_selector('div:has-text("ID:")', timeout=15000)
            except:
                print("لم تظهر النتائج فوراً، جاري المحاولة اليدوية...")
                # إذا لم تظهر، نحاول الكتابة في مربع البحث والضغط انتر
                # (هذا الجزء متقدم ويعتمد على selectors، لكن سنكتفي بإعادة المحاولة حالياً)
                return {"status": "empty", "msg": "الصفحة فتحت لكن النتائج بيضاء (ربما النت بطيء). حاول مرة أخرى."}

            # 4. استخراج النصوص (الحصاد)
            ads_texts = page.evaluate("""() => {
                // نأخذ كل العناصر التي تحتوي على نص "ID:"
                const divs = Array.from(document.querySelectorAll('div'));
                const cards = divs.filter(d => d.innerText.includes('ID:') && d.innerText.length > 30 && d.innerText.length < 500);
                
                // تنظيف التكرار
                const uniqueTexts = [...new Set(cards.map(c => c.innerText))];
                return uniqueTexts.slice(0, 5); // أول 5 نتائج
            }""")

            if len(ads_texts) == 0:
                return {"status": "empty", "msg": "لم نجد إعلانات تحتوي نصوصاً واضحة."}

            return {"status": "success", "count": len(ads_texts), "data": ads_texts}

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
