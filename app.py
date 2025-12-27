
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
    db = client.get_database()
    sources_col = db['sources']
    ads_col = db['ads']
    client.admin.command('ping')
    print("✅ Connected to MongoDB")
except Exception as e:
    print(f"❌ MongoDB Error: {e}")
    sources_col = ads_col = None

def get_clean_m3u(url):
    try:
        # استخدام User-Agent لإيهام السيرفر الأصلي أننا متصفح
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        r = requests.get(url, headers=headers, timeout=15, stream=True)
        if r.status_code == 200:
            lines = []
            for line in r.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8', errors='ignore')
                    if "#EXTM3U" not in decoded_line: # نتجاهل رأس الملف لتجنب التكرار
                        lines.append(decoded_line)
            return lines
    except Exception as e:
        print(f"⚠️ Error fetching {url}: {e}")
    return []

# --- لوحة التحكم (نفس التصميم السابق مع تحسينات) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IPTV Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-white p-4">
    <div class="max-w-md mx-auto">
        <h1 class="text-2xl font-bold mb-6 border-b pb-2">💎 لوحة تحكم النخبة</h1>
        
        <form action="/admin/add_ad" method="POST" class="bg-gray-800 p-4 rounded-xl mb-6">
            <input name="name" placeholder="اسم الإعلان" class="w-full p-2 mb-2 bg-gray-700 rounded text-sm" required>
            <input name="url" placeholder="رابط الأفلييت" class="w-full p-2 mb-2 bg-gray-700 rounded text-sm" required>
            <input name="logo" placeholder="رابط الأيقونة (اختياري)" class="w-full p-2 mb-2 bg-gray-700 rounded text-sm">
            <button class="w-full bg-blue-600 p-2 rounded font-bold">زرع إعلان</button>
        </form>

        <form action="/admin/add_source" method="POST" class="bg-gray-800 p-4 rounded-xl mb-6">
            <input name="url" placeholder="رابط M3U الأصلي" class="w-full p-2 mb-2 bg-gray-700 rounded text-sm" required>
            <button class="w-full bg-green-600 p-2 rounded font-bold">إضافة مصدر قنوات</button>
        </form>

        <div class="text-xs bg-black p-3 rounded border border-gray-700">
            <p class="text-gray-400">رابطك للمشتركين:</p>
            <p class="text-blue-400 font-mono mt-1 break-all">{{ host_url }}playlist.m3u</p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/admin')
def admin():
    if request.args.get('pw') != ADMIN_PASSWORD: return "Forbidden", 403
    ads = list(ads_col.find()) if ads_col else []
    sources = list(sources_col.find()) if sources_col else []
    return render_template_string(HTML_TEMPLATE, ads=ads, sources=sources, host_url=request.host_url)

@app.route('/admin/add_ad', methods=['POST'])
def add_ad():
    if ads_col is not None:
        ads_col.insert_one({"name": request.form['name'], "url": request.form['url'], "logo": request.form['logo'] or "https://bit.ly/3vL9Y7m", "clicks": 0})
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
        # 1. حقن الإعلانات
        if ads_col is not None:
            for ad in ads_col.find():
                yield f'#EXTINF:-1 tvg-logo="{ad["logo"]}", {ad["name"]}\n'
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
