import os, requests, re, json
from flask import Flask, render_template_string, request, redirect, jsonify, Response
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

# --- إعدادات القاعدة ---
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

def fetch_m3u_content(url):
    try:
        # استخدام User-Agent قوي جداً لتخطي حظر السيرفرات
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*'
        }
        r = requests.get(url, headers=headers, timeout=20, verify=False)
        if r.status_code == 200:
            # تنظيف المحتوى من أي فراغات زائدة
            content = r.text.strip()
            if "#EXTM3U" in content:
                # نأخذ القنوات فقط ونحذف الرأس الأول لتجنب التكرار
                lines = content.splitlines()
                return "\n".join(lines[1:]) if "#EXTM3U" in lines[0] else content
    except Exception as e:
        print(f"Fetch Error: {e}")
    return ""

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IPTV Admin</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-white font-sans p-4">
    <div class="max-w-md mx-auto">
        <h1 class="text-xl font-bold mb-6 text-center text-blue-400">💎 لوحة تحكم النخبة v4.0</h1>
        
        <form action="/admin/add_ad" method="POST" class="bg-gray-800 p-4 rounded-2xl mb-4 border border-gray-700">
            <input name="name" placeholder="اسم الإعلان" class="w-full p-2 mb-2 bg-gray-700 rounded-xl text-sm" required>
            <input name="url" placeholder="رابط الأفلييت" class="w-full p-2 mb-2 bg-gray-700 rounded-xl text-sm" required>
            <button class="w-full bg-blue-600 py-2 rounded-xl font-bold">حفظ الإعلان</button>
        </form>

        <form action="/admin/add_source" method="POST" class="bg-gray-800 p-4 rounded-2xl mb-4 border border-gray-700">
            <input name="url" placeholder="رابط M3U (ينتهي بـ type=m3u)" class="w-full p-2 mb-2 bg-gray-700 rounded-xl text-sm" required>
            <button class="w-full bg-green-600 py-2 rounded-xl font-bold">إضافة مصدر القنوات</button>
        </form>

        <div class="bg-black p-3 rounded-xl border border-gray-800 text-center">
            <p class="text-gray-500 text-xs">الرابط النهائي للنشر:</p>
            <p class="text-blue-500 text-xs mt-2 font-mono break-all">{{ host_url }}playlist.m3u</p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/admin')
def admin():
    if request.args.get('pw') != ADMIN_PASSWORD: return "Forbidden", 403
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
        yield "#EXTM3U\n"
        # 1. حقن الإعلانات
        if ads_col is not None:
            for ad in ads_col.find():
                yield f'#EXTINF:-1 tvg-logo="{ad.get("logo")}", {ad.get("name")}\n'
                yield f'{request.host_url.rstrip("/")}/go/{ad["_id"]}\n'
        
        # 2. جلب المصادر
        if sources_col is not None:
            for src in sources_col.find():
                yield fetch_m3u_content(src['url']) + "\n"

    # استخدام Mimetype الصحيح الذي تطلبه تطبيقات IPTV
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
