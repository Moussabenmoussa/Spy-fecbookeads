
import os, requests, re, json
from flask import Flask, render_template_string, request, redirect, jsonify, Response
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

# --- تنظيف وإعداد قاعدة البيانات ---
raw_uri = os.getenv("MONGO_URI", "").strip()
MONGO_URI = re.sub(r'[\s\n\r]', '', raw_uri)
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123").strip()

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000)
    db = client['iptv_db'] 
    sources_col = db['sources']
    ads_col = db['ads']
    client.admin.command('ping')
except:
    sources_col = ads_col = None

# --- دالة جلب القنوات بنظام التدفق (Streaming) ---
def stream_m3u_source(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        # فتح اتصال مع الرابط الأصلي بنظام التدفق
        with requests.get(url, headers=headers, timeout=30, stream=True, verify=False) as r:
            if r.status_code == 200:
                for line in r.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8', errors='ignore')
                        # نتجاهل السطر الأول لكي لا يتكرر #EXTM3U
                        if not decoded_line.startswith("#EXTM3U"):
                            yield decoded_line + "\n"
    except Exception as e:
        print(f"Error streaming source: {e}")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IPTV Dashboard Pro</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-900 text-slate-200 font-sans p-4">
    <div class="max-w-md mx-auto">
        <header class="text-center mb-8">
            <h1 class="text-2xl font-black text-blue-500 shadow-sm">💎 IPTV GATEWAY v5.0</h1>
            <p class="text-slate-500 text-xs mt-1 font-mono">نظام حقن الإعلانات وإدارة الترافيك</p>
        </header>

        <form action="/admin/add_ad" method="POST" class="bg-slate-800 p-5 rounded-3xl shadow-xl mb-6 border border-slate-700">
            <h2 class="text-sm font-bold mb-4 text-blue-400">📢 إضافة إعلان (قناة حقن)</h2>
            <input name="name" placeholder="اسم الإعلان (مثلاً: 🎁 هديتك هنا)" class="w-full p-3 mb-3 bg-slate-900 rounded-2xl text-sm border border-slate-700 focus:border-blue-500 outline-none" required>
            <input name="url" placeholder="رابط الأفلييت (AliExpress/CPA)" class="w-full p-3 mb-4 bg-slate-900 rounded-2xl text-sm border border-slate-700 focus:border-blue-500 outline-none" required>
            <button class="w-full bg-blue-600 hover:bg-blue-700 py-3 rounded-2xl font-black transition shadow-lg shadow-blue-900/20">حفظ الإعلان</button>
        </form>

        <form action="/admin/add_source" method="POST" class="bg-slate-800 p-5 rounded-3xl shadow-xl mb-8 border border-slate-700">
            <h2 class="text-sm font-bold mb-4 text-green-400">🔗 إضافة مصدر قنوات الأصلي</h2>
            <input name="url" placeholder="ألصق رابط M3U هنا" class="w-full p-3 mb-4 bg-slate-900 rounded-2xl text-sm border border-slate-700 focus:border-green-500 outline-none" required>
            <button class="w-full bg-green-600 hover:bg-green-700 py-3 rounded-2xl font-black transition shadow-lg shadow-green-900/20">تفعيل المصدر</button>
        </form>

        <div class="bg-black/50 p-4 rounded-3xl border border-slate-800">
            <p class="text-slate-500 text-[10px] text-center mb-2">رابطك العالمي للنشر (19k مشترك):</p>
            <p class="text-blue-400 text-[11px] font-mono break-all text-center">{{ host_url }}playlist.m3u</p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/admin')
def admin():
    if request.args.get('pw') != ADMIN_PASSWORD: return "Access Denied", 403
    return render_template_string(HTML_TEMPLATE, host_url=request.host_url)

@app.route('/admin/add_ad', methods=['POST'])
def add_ad():
    if ads_col is not None:
        ads_col.insert_one({"name": request.form['name'], "url": request.form['url'], "logo": "https://cdn-icons-png.flaticon.com/512/743/743224.png", "clicks": 0})
    return redirect(f'/admin?pw={ADMIN_PASSWORD}')

@app.route('/admin/add_source', methods=['POST'])
def add_source():
    if sources_col is not None:
        sources_col.insert_one({"url": request.form['url'].strip()})
    return redirect(f'/admin?pw={ADMIN_PASSWORD}')

@app.route('/playlist.m3u')
def get_playlist():
    def generate():
        # الرأس الأساسي
        yield "#EXTM3U\n"
        
        # 1. حقن الإعلانات المحفوظة في MongoDB
        if ads_col is not None:
            for ad in ads_col.find():
                yield f'#EXTINF:-1 tvg-logo="{ad.get("logo")}", {ad.get("name")}\n'
                yield f'{request.host_url.rstrip("/")}/go/{ad["_id"]}\n'
        
        # 2. حقن القنوات من المصادر الأصلية (Streaming)
        if sources_col is not None:
            for src in sources_col.find():
                for line in stream_m3u_source(src['url']):
                    yield line

    # إرجاع الاستجابة بصيغة M3U الرسمية لتقبلها التطبيقات
    return Response(generate(), mimetype='application/x-mpegurl')

@app.route('/go/<id>')
def go_to_ad(id):
    if ads_col is not None:
        ad = ads_col.find_one_and_update({"_id": ObjectId(id)}, {"$inc": {"clicks": 1}})
        if ad: return redirect(ad['url'])
    return "Not Found", 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
