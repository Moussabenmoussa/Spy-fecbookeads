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
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    # تحديد اسم قاعدة البيانات صراحة لحل مشكلة No default database
    db = client['iptv_db'] 
    sources_col = db['sources']
    ads_col = db['ads']
    client.admin.command('ping')
    print("✅ Connected to MongoDB")
except Exception as e:
    print(f"❌ MongoDB Error: {e}")
    sources_col = ads_col = None

def get_clean_m3u(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        r = requests.get(url, headers=headers, timeout=15, stream=True)
        if r.status_code == 200:
            lines = []
            for line in r.iter_lines():
                if line:
                    try:
                        decoded_line = line.decode('utf-8', errors='ignore')
                        if "#EXTM3U" not in decoded_line:
                            lines.append(decoded_line)
                    except: continue
            return lines
    except Exception as e:
        print(f"⚠️ Error fetching {url}: {e}")
    return []

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IPTV Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-white p-4 font-sans">
    <div class="max-w-md mx-auto">
        <h1 class="text-2xl font-bold mb-6 border-b border-gray-700 pb-2 text-blue-400 text-center">💎 لوحة تحكم النخبة</h1>
        
        <form action="/admin/add_ad" method="POST" class="bg-gray-800 p-4 rounded-2xl shadow-lg mb-6 border border-gray-700">
            <h2 class="text-sm font-bold mb-3 text-gray-400">📢 إضافة إعلان جديد</h2>
            <input name="name" placeholder="اسم الإعلان" class="w-full p-3 mb-2 bg-gray-700 rounded-xl text-sm outline-none border border-transparent focus:border-blue-500" required>
            <input name="url" placeholder="رابط الأفلييت (AliExpress/CPA)" class="w-full p-3 mb-2 bg-gray-700 rounded-xl text-sm outline-none border border-transparent focus:border-blue-500" required>
            <input name="logo" placeholder="رابط الأيقونة (اختياري)" class="w-full p-3 mb-3 bg-gray-700 rounded-xl text-sm outline-none border border-transparent focus:border-blue-500">
            <button class="w-full bg-blue-600 hover:bg-blue-700 py-3 rounded-xl font-bold transition">زرع إعلان في القائمة</button>
        </form>

        <form action="/admin/add_source" method="POST" class="bg-gray-800 p-4 rounded-2xl shadow-lg mb-6 border border-gray-700">
            <h2 class="text-sm font-bold mb-3 text-gray-400">🔗 إضافة مصدر قنوات (M3U)</h2>
            <input name="url" placeholder="رابط M3U الأصلي" class="w-full p-3 mb-3 bg-gray-700 rounded-xl text-sm outline-none border border-transparent focus:border-green-500" required>
            <button class="w-full bg-green-600 hover:bg-green-700 py-3 rounded-xl font-bold transition text-white">إضافة مصدر جديد</button>
        </form>

        <div class="bg-black p-4 rounded-2xl border border-gray-800 shadow-inner">
            <p class="text-gray-500 text-xs">رابطك الذي ستنشره للمشتركين:</p>
            <p class="text-blue-500 font-mono text-xs mt-2 break-all p-2 bg-gray-900 rounded border border-gray-800">{{ host_url }}playlist.m3u</p>
        </div>
        
        <div class="mt-6">
            <h2 class="text-sm font-bold mb-3 text-gray-400">📋 الإعلانات الحالية</h2>
            {% for ad in ads %}
            <div class="bg-gray-800 p-3 rounded-xl mb-2 flex justify-between items-center text-xs">
                <span>{{ ad['name'] }}</span>
                <span class="text-blue-400">نقرات: {{ ad['clicks'] }}</span>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

@app.route('/admin')
def admin():
    if request.args.get('pw') != ADMIN_PASSWORD: return "Forbidden", 403
    ads = list(ads_col.find()) if ads_col is not None else []
    sources = list(sources_col.find()) if sources_col is not None else []
    return render_template_string(HTML_TEMPLATE, ads=ads, sources=sources, host_url=request.host_url)

@app.route('/admin/add_ad', methods=['POST'])
def add_ad():
    if ads_col is not None:
        ads_col.insert_one({
            "name": request.form['name'], 
            "url": request.form['url'], 
            "logo": request.form['logo'] or "https://cdn-icons-png.flaticon.com/512/743/743224.png", 
            "clicks": 0
        })
    return redirect(f'/admin?pw={ADMIN_PASSWORD}')

@app.route('/admin/add_source', methods=['POST'])
def add_source():
    if sources_col is not None:
        sources_col.insert_one({"url": request.form['url'].strip()})
    return redirect(f'/admin?pw={ADMIN_PASSWORD}')

@app.route('/playlist.m3u')
def get_playlist():
    def generate():
        yield "#EXTM3U\n"
        # 1. حقن الإعلانات باستخدام bracket notation لتجنب AttributeError
        if ads_col is not None:
            for ad in ads_col.find():
                logo = ad.get('logo', 'https://cdn-icons-png.flaticon.com/512/743/743224.png')
                name = ad.get('name', 'Ad')
                yield f'#EXTINF:-1 tvg-logo="{logo}", {name}\n'
                yield f'{request.host_url.rstrip("/")}/go/{ad["_id"]}\n'
        
        # 2. جلب ودمج المصادر
        if sources_col is not None:
            for src in sources_col.find():
                channels = get_clean_m3u(src['url'])
                for ch in channels:
                    yield ch + "\n"

    return Response(generate(), mimetype='text/plain')

@app.route('/go/<id>')
def go_to_ad(id):
    if ads_col is not None:
        ad = ads_col.find_one_and_update({"_id": ObjectId(id)}, {"$inc": {"clicks": 1}})
        if ad: return redirect(ad['url'])
    return "Not Found", 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
