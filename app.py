import os, requests, re, json
from flask import Flask, render_template_string, request, redirect, jsonify, Response
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

# --- 1. إعدادات قاعدة البيانات والتنظيف ---
raw_uri = os.getenv("MONGO_URI", "").strip()
MONGO_URI = re.sub(r'[\s\n\r]', '', raw_uri)
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123").strip()

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=15000)
    # استخدام قاعدة بيانات محددة لضمان استقرار الاتصال
    db = client['iptv_db'] 
    sources_col = db['sources']
    ads_col = db['ads']
    client.admin.command('ping')
except Exception as e:
    sources_col = ads_col = None

# --- 2. محرك جلب البيانات وتوافقية الـ IPTV ---
def get_external_m3u(url):
    try:
        # إيهام السيرفر الأصلي أننا متصفح ويندوز حقيقي لتخطي الحظر
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*'
        }
        r = requests.get(url.strip(), headers=headers, timeout=20)
        if r.status_code == 200:
            content = r.text
            # حذف سطر EXTM3U من المصدر لتجنب تكراره في الملف النهائي
            lines = content.splitlines()
            cleaned_lines = []
            for line in lines:
                if "#EXTM3U" not in line and line.strip():
                    cleaned_lines.append(line.strip())
            return "\r\n".join(cleaned_lines)
    except:
        pass
    return ""

# --- 3. تصميم لوحة التحكم (Dark Mode - Mobile First) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IPTV Master Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-black text-gray-200 font-sans p-4">
    <div class="max-w-md mx-auto">
        <header class="text-center py-6 border-b border-gray-800 mb-6">
            <h1 class="text-2xl font-black text-blue-500">IPTV GATEWAY PRO</h1>
            <p class="text-gray-500 text-[10px] uppercase tracking-tighter">Powered by Render & MongoDB</p>
        </header>

        <form action="/admin/add_ad" method="POST" class="bg-gray-900 p-5 rounded-3xl mb-4 border border-gray-800">
            <h2 class="text-blue-400 text-xs font-bold mb-3 uppercase">📢 حقن إعلان جديد</h2>
            <input name="name" placeholder="اسم الإعلان (مثلاً: 🎁 هدية اليوم)" class="w-full p-3 mb-2 bg-black rounded-xl text-sm border border-gray-800 focus:border-blue-500 outline-none" required>
            <input name="url" placeholder="رابط الأفلييت / CPA" class="w-full p-3 mb-3 bg-black rounded-xl text-sm border border-gray-800 focus:border-blue-500 outline-none" required>
            <button class="w-full bg-blue-600 py-3 rounded-xl font-bold text-sm">إضافة للقائمة</button>
        </form>

        <form action="/admin/add_source" method="POST" class="bg-gray-900 p-5 rounded-3xl mb-6 border border-gray-800">
            <h2 class="text-green-400 text-xs font-bold mb-3 uppercase">🔗 ربط مصدر قنوات</h2>
            <input name="url" placeholder="رابط M3U الأصلي" class="w-full p-3 mb-3 bg-black rounded-xl text-sm border border-gray-800 focus:border-green-500 outline-none" required>
            <button class="w-full bg-green-600 py-3 rounded-xl font-bold text-sm">تفعيل المصدر</button>
        </form>

        <div class="bg-blue-900/10 p-4 rounded-3xl border border-blue-900/30 text-center mb-10">
            <p class="text-[10px] text-gray-500 mb-2">رابط النشر في تلجرام:</p>
            <p class="text-[11px] font-mono text-blue-400 break-all">{{ host_url }}playlist.m3u</p>
        </div>
    </div>
</body>
</html>
"""

# --- 4. المسارات والمنطق (Routes) ---

@app.route('/admin')
def admin():
    if request.args.get('pw') != ADMIN_PASSWORD:
        return "Unauthorized", 403
    return render_template_string(HTML_TEMPLATE, host_url=request.host_url)

@app.route('/admin/add_ad', methods=['POST'])
def add_ad():
    if ads_col is not None:
        ads_col.insert_one({"name": request.form['name'], "url": request.form['url'], "clicks": 0})
    return redirect(f'/admin?pw={ADMIN_PASSWORD}')

@app.route('/admin/add_source', methods=['POST'])
def add_source():
    if sources_col is not None:
        sources_col.insert_one({"url": request.form['url'].strip()})
    return redirect(f'/admin?pw={ADMIN_PASSWORD}')

# --- المسار الرئيسي الذي يطلبه التطبيق (The M3U Generator) ---
@app.route('/playlist.m3u')
def get_playlist():
    def generate():
        # 1. رأس الملف بتنسيق M3U القياسي مع سطر فارغ
        yield "#EXTM3U\r\n\r\n"
        
        # 2. قناة فحص ثابتة للتأكد من أن الرابط يعمل في التطبيق
        yield '#EXTINF:-1 tvg-logo="https://bit.ly/3vL9Y7m", [✅ SERVER ACTIVE]\r\n'
        yield 'http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4\r\n\r\n'

        # 3. حقن الإعلانات من قاعدة البيانات
        if ads_col is not None:
            for ad in ads_col.find():
                name = ad.get('name', 'Ad')
                ad_id = str(ad['_id'])
                # رابط تتبع النقرة
                click_url = f"{request.host_url.rstrip('/')}/go/{ad_id}"
                yield f'#EXTINF:-1 tvg-logo="https://cdn-icons-png.flaticon.com/512/743/743224.png", {name}\r\n'
                yield f'{click_url}\r\n\r\n'
        
        # 4. دمج القنوات من المصادر الأصلية
        if sources_col is not None:
            for src in sources_col.find():
                content = get_external_m3u(src['url'])
                if content:
                    yield content + "\r\n"

    # أهم جزء: إرسال الـ Headers التي تجبر التطبيق على قبول الملف كـ M3U
    response_headers = {
        'Content-Type': 'application/x-mpegurl',
        'Content-Disposition': 'attachment; filename="playlist.m3u"',
        'Connection': 'keep-alive',
        'Access-Control-Allow-Origin': '*'
    }
    
    return Response(generate(), headers=response_headers)

@app.route('/go/<id>')
def go_to_ad(id):
    if ads_col is not None:
        ad = ads_col.find_one_and_update({"_id": ObjectId(id)}, {"$inc": {"clicks": 1}})
        if ad:
            return redirect(ad['url'])
    return "Not Found", 404

if __name__ == '__main__':
    # الحصول على المنفذ من ريندر أو استخدام 10000
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
