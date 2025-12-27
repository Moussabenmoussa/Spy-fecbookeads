import os, requests, time, re
from flask import Flask, render_template_string, request, redirect, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

# --- الإعدادات وقاعدة البيانات ---
MONGO_URI = os.getenv("MONGO_URI", "").strip()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123") # كلمة السر للوحة التحكم
client = MongoClient(MONGO_URI)
db = client['iptv_manager']
sources_col = db['sources']
ads_col = db['ads']
stats_col = db['stats']

# --- وظائف مساعدة ---
def get_clean_m3u(url):
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            lines = r.text.splitlines()
            if lines and "#EXTM3U" in lines[0]:
                return lines[1:] # نرجع القنوات بدون رأس الملف
    except: pass
    return []

# --- لوحة التحكم (Dashboard UI) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IPTV Master Control</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-white font-sans">
    <div class="max-w-md mx-auto p-4">
        <header class="flex justify-between items-center mb-8 bg-gray-800 p-4 rounded-2xl shadow-lg border-b-2 border-blue-500">
            <h1 class="text-xl font-bold">💎 رادار النخبة</h1>
            <span class="bg-green-500 text-xs px-2 py-1 rounded-full text-black font-bold">Online</span>
        </header>

        <!-- إدارة الإعلانات -->
        <section class="mb-8">
            <h2 class="text-blue-400 font-bold mb-4 flex items-center">📢 إدارة الإعلانات المحقونة</h2>
            <form action="/admin/add_ad" method="POST" class="bg-gray-800 p-4 rounded-2xl space-y-3">
                <input name="name" placeholder="اسم قناة الإعلان (مثلا: هديتك هنا)" class="w-full p-3 bg-gray-700 rounded-xl border border-gray-600 focus:outline-none focus:border-blue-500 text-sm">
                <input name="url" placeholder="رابط الإعلان (AliExpress / CPA)" class="w-full p-3 bg-gray-700 rounded-xl border border-gray-600 focus:outline-none focus:border-blue-500 text-sm">
                <input name="logo" placeholder="رابط أيقونة القناة (Image URL)" class="w-full p-3 bg-gray-700 rounded-xl border border-gray-600 focus:outline-none focus:border-blue-500 text-sm">
                <button class="w-full bg-blue-600 py-3 rounded-xl font-bold hover:bg-blue-700 transition">زرع إعلان جديد</button>
            </form>
            
            <div class="mt-4 space-y-2">
                {% for ad in ads %}
                <div class="flex justify-between items-center bg-gray-800 p-3 rounded-xl border-r-4 border-blue-500">
                    <div class="text-sm font-bold">{{ ad.name }} <span class="text-xs text-gray-500 block">نقر: {{ ad.clicks }}</span></div>
                    <a href="/admin/delete_ad/{{ ad._id }}" class="text-red-500 text-xs">حذف</a>
                </div>
                {% endfor %}
            </div>
        </section>

        <!-- إدارة المصادر M3U -->
        <section class="mb-8">
            <h2 class="text-green-400 font-bold mb-4 flex items-center">🔗 مصادر M3U المتصلة</h2>
            <form action="/admin/add_source" method="POST" class="bg-gray-800 p-4 rounded-2xl space-y-3">
                <input name="url" placeholder="رابط m3u الأصلي" class="w-full p-3 bg-gray-700 rounded-xl border border-gray-600 focus:outline-none focus:border-green-500 text-sm">
                <button class="w-full bg-green-600 py-3 rounded-xl font-bold hover:bg-green-700 transition">إضافة مصدر جديد</button>
            </form>

            <div class="mt-4 space-y-2">
                {% for src in sources %}
                <div class="flex justify-between items-center bg-gray-800 p-3 rounded-xl border-r-4 border-green-500">
                    <div class="text-xs truncate w-48">{{ src.url }}</div>
                    <a href="/admin/delete_source/{{ src._id }}" class="text-red-500 text-xs">إزالة</a>
                </div>
                {% endfor %}
            </div>
        </section>

        <footer class="text-center text-gray-600 text-xs mt-10">
            <p>رابطك للمشتركين:</p>
            <code class="block bg-black p-2 rounded mt-2 text-blue-400">{{ base_url }}/playlist.m3u</code>
        </footer>
    </div>
</body>
</html>
"""

# --- المسارات (Routes) ---

@app.route('/admin')
def admin():
    # حماية بسيطة بكلمة سر عبر الـ URL لسهولة الهاتف
    pw = request.args.get('pw')
    if pw != ADMIN_PASSWORD:
        return "غير مصرح لك", 403
    
    ads = list(ads_col.find())
    sources = list(sources_col.find())
    base_url = request.host_url.rstrip('/')
    return render_template_string(HTML_TEMPLATE, ads=ads, sources=sources, base_url=base_url)

@app.route('/admin/add_ad', methods=['POST'])
def add_ad():
    ads_col.insert_one({
        "name": request.form['name'],
        "url": request.form['url'],
        "logo": request.form['logo'],
        "clicks": 0
    })
    return redirect(f'/admin?pw={ADMIN_PASSWORD}')

@app.route('/admin/add_source', methods=['POST'])
def add_source():
    sources_col.insert_one({"url": request.form['url']})
    return redirect(f'/admin?pw={ADMIN_PASSWORD}')

@app.route('/admin/delete_ad/<id>')
def delete_ad(id):
    ads_col.delete_one({"_id": ObjectId(id)})
    return redirect(f'/admin?pw={ADMIN_PASSWORD}')

@app.route('/admin/delete_source/<id>')
def delete_source(id):
    sources_col.delete_one({"_id": ObjectId(id)})
    return redirect(f'/admin?pw={ADMIN_PASSWORD}')

# --- محرك الحقن (The Injector Engine) ---
@app.route('/playlist.m3u')
def get_playlist():
    output = ["#EXTM3U"]
    
    # 1. حقن الإعلانات
    ads = list(ads_col.find())
    for ad in ads:
        output.append(f'#EXTINF:-1 tvg-logo="{ad.logo}", {ad.name}')
        output.append(f'{request.host_url.rstrip("/")}/go/{ad._id}')
    
    # 2. جلب ودمج القنوات من المصادر
    sources = list(sources_col.find())
    for src in sources:
        channels = get_clean_m3u(src.url)
        output.extend(channels)
    
    return "\n".join(output), {"Content-Type": "text/plain; charset=utf-8"}

# --- محول النقرات (Click Handler) ---
@app.route('/go/<id>')
def go_to_ad(id):
    ad = ads_col.find_one_and_update(
        {"_id": ObjectId(id)},
        {"$inc": {"clicks": 1}}
    )
    if ad:
        # هنا يمكنك إضافة "صفحة غسيل المرجع" إذا أردت
        return redirect(ad['url'])
    return "Ad not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
