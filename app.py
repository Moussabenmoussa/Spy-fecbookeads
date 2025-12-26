
import os
import base64
from flask import Flask, jsonify, request, render_template_string
from playwright.sync_api import sync_playwright

app = Flask(__name__)

# --- واجهة "غرفة التحكم" ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DZ Ad Hunter - Debug Mode 📸</title>
    <style>
        body { font-family: sans-serif; background: #222; color: #fff; text-align: center; padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; }
        input { padding: 15px; width: 60%; border-radius: 5px; border: none; }
        button { padding: 15px 30px; background-color: #e63946; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }
        .screenshot-box { margin-top: 20px; border: 2px solid #555; padding: 10px; background: #000; min-height: 300px; }
        img { max-width: 100%; height: auto; display: block; margin: 0 auto; }
        .status { margin: 15px; color: #ffd700; }
    </style>
</head>
<body>
<div class="container">
    <h1>📸 وضع التشخيص (X-Ray)</h1>
    <p>هذا الوضع سيرينا بالضبط ما يراه الروبوت داخل السيرفر</p>
    
    <div>
        <input type="text" id="keyword" placeholder="اكتب كلمة واحدة (مثلاً: ساعة)...">
        <button onclick="startDebug()" id="btn">التقط صورة</button>
    </div>

    <p class="status" id="statusMsg"></p>
    
    <div class="screenshot-box" id="resultBox">
        <p style="color:#777; padding-top: 100px;">الصورة ستظهر هنا...</p>
    </div>
</div>

<script>
    async function startDebug() {
        const keyword = document.getElementById('keyword').value;
        const btn = document.getElementById('btn');
        const status = document.getElementById('statusMsg');
        const box = document.getElementById('resultBox');

        if (!keyword) return;

        btn.disabled = true;
        status.innerText = "الروبوت يفتح الكاميرا... (انتظر 30 ثانية)";
        box.innerHTML = '<p style="color:#777; padding-top: 100px;">جاري التصوير...</p>';

        try {
            const response = await fetch(`/debug?q=${keyword}`);
            const json = await response.json();

            if (json.status === "success") {
                status.innerText = `✅ تم التقاط الصورة! (العنوان: ${json.title})`;
                // عرض الصورة القادمة من السيرفر (Base64)
                box.innerHTML = `<img src="data:image/png;base64,${json.image}" alt="Screenshot">`;
            } else {
                status.innerText = `❌ خطأ: ${json.error}`;
            }
        } catch (err) {
            status.innerText = "❌ حدث خطأ في الاتصال بالسيرفر.";
        } finally {
            btn.disabled = false;
        }
    }
</script>
</body>
</html>
"""

def take_screenshot(keyword):
    print(f"📸 تشخيص المشكلة عن: {keyword}...")
    
    with sync_playwright() as p:
        # إعدادات المتصفح
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        )
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()

        try:
            # الذهاب للرابط
            url = f"https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=DZ&q={keyword}"
            page.goto(url, timeout=60000)
            
            # ننتظر قليلاً ليتحمل المحتوى (مهما كان)
            page.wait_for_timeout(8000)
            
            # التقاط الصورة
            screenshot_bytes = page.screenshot(full_page=False)
            
            # تحويل الصورة لنص (Base64) لإرسالها للمتصفح
            base64_img = base64.b64encode(screenshot_bytes).decode('utf-8')
            
            return {
                "status": "success", 
                "title": page.title(),
                "image": base64_img
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}
        finally:
            browser.close()

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/debug', methods=['GET'])
def debug_endpoint():
    query = request.args.get('q', 'Livraison')
    return jsonify(take_screenshot(query))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
