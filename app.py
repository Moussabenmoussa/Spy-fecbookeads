
import os, requests, re, json
from flask import Flask, render_template_string, request, redirect, jsonify, Response
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

# --- 1. إعدادات قاعدة البيانات والأمان ---
raw_uri = os.getenv("MONGO_URI", "").strip()
# تنظيف الرابط من أي مسافات مخفية قد تأتي من الهاتف
MONGO_URI = re.sub(r'[\s\n\r]', '', raw_uri)
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123").strip()

try:
    # الاتصال بـ MongoDB مع تحديد اسم قاعدة البيانات iptv_db
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000)
    db = client['iptv_db'] 
    sources_col = db['sources']
    ads_col = db['ads']
    client.admin.command('ping')
    print("✅ Connected to MongoDB Successfully")
except Exception as e:
    print(f"❌ MongoDB Connection Error: {e}")
    sources_col = ads_col = None

# --- 2. محرك جلب القنوات (تخطي الحماية + Streaming) ---
def stream_m3u_source(url):
    try:
        # إيهام السيرفر الأصلي أن الطلب قادم من تطبيق أندرويد حقيقي
        headers = {
            'User-Agent': 'IPTVBox/1.4 (Linux; Android 11; SmartTV)',
            'Accept': '*/*'
        }
        # جلب البيانات بنظام التدفق (Stream) لتوفير الرام في Render
        with requests.get(url.strip(), headers=headers, timeout=25, stream=True, verify=False) as r:
            if r.status_code == 200:
                for line in r.iter_lines():
                    if line:
                        decoded = line.decode('utf-8', errors='ignore').strip()
                        # تخطي سطر البداية لتجنب تكراره في القائمة النهائية
                        if decoded and not decoded.startswith("#EXTM3U"):
                            yield decoded + "\n"
            else:
                yield f'#EXTINF:-1, [⚠️ خطأ من المصدر: {r.status_code}]\n'
                yield f'http://error.com/{r.status_code}.mp4\n'
    except Exception as e:
        yield f'#EXTINF:-1, [⚠️ فشل الاتصال بالمصدر الأصلي]\n'
        yield 'http://error.com/timeout.mp4\n'

# --- 3. تصميم لوحة التحكم (Mobile-First UI) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IPTV Control Center</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style> .glass { background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(10px); } </style>
</head>
<body class="bg-slate-950 text-slate-200 font-sans p-4 min-h-screen">
    <div class="max-w-md mx-auto">
        <header class="text-center py-6">
            <h1 class="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400">💎 رادار النخبة</h1>
            <p class="text-slate-500 text-[10px] tracking-widest mt-1 uppercase">Advanced IPTV Injection System</p>
        </header>

        <!-- قسم الإعلانات -->
        <div class="glass p-5 rounded-[2rem] border border-slate-800 shadow-2xl mb-6">
            <h2 class="text-blue-400 text-sm font-bold mb-4 flex items-center">📢 حقن الإعلانات (CPA / AliExpress)</h2>
            <form action="/admin/add_ad" method="POST" class="space-y-3">
                <input name="name" placeholder="اسم الإعلان (مثلاً: 🎁 هديتك هنا)" class="w-full p-3 bg-slate-900/50 rounded-2xl text-sm border border-slate-700 focus:border-blue-500 outline-none transition" required>
                <input name="url" placeholder="رابط العرض الربحي" class="w-full p-3 bg-slate-900/50 rounded-2xl text-sm border border-slate-700 focus:border-blue-500 outline-none" required>
                <button class="w-full bg-blue-600 hover:bg-blue-500 py-4 rounded-2xl font-black text-sm shadow-lg shadow-blue-900/20 transition-all active:scale-95">زرع الإعلان في القائمة</button>
            </form>
        </div>

        <!-- قسم المصادر -->
        <div class="glass p-5 rounded-[2rem] border border-slate-800 shadow-2xl mb-6">
            <h2 class="text-emerald-400 text-sm font-bold mb-4 flex items-center">🔗 مصادر M3U المتصلة</h2>
            <form action="/admin/add_source" method="POST" class="space-y-3">
                <input name="url" placeholder="رابط M3U الأصلي" class="w-full p-3 bg-slate-900/50 rounded-2xl text-sm border border-slate-700 focus:border-emerald-500 outline-none" required>
                <button class="w-full bg-emerald-600 hover:bg-emerald-500 py-4 rounded-2xl font-black text-sm shadow-lg shadow-emerald-900/20 transition-all active:scale-95">ربط مصدر جديد</button>
            </form>
        </div>

        <!-- قائمة الإعلانات الحالية -->
        <div class="space-y-3 mb-10">
            <h3 class="text-slate-500 text-xs font-bold px-2">الإعلانات النشطة حالياً:</h3>
            {% for ad in ads %}
            <div class="bg-slate-900/80 p-4 rounded-2xl flex justify-between items-center border border-slate-800">
                <div>
                    <div class="font-bold text-sm">{{ ad['name'] }}</div>
                    <div class="text-[10px] text-blue-500 uppercase font-bold mt-1">Clicks: {{ ad['clicks'] }}</div>
                </div>
                <a href="/admin/delete_ad/{{ ad['_id'] }}" class="text-red-500 bg-red-500/10 p-2 rounded-lg">🗑️</a>
            </div>
            {% endfor %}
        </div>

        <!-- الروابط النهائية -->
        <div class="bg-blue-600/10 border border-blue-500/20 p-4 rounded-3xl text-center">
            <p class="text-[10px] text-blue-400 mb-2">رابط النشر في تلجرام (19k مشترك):</p>
            <p class="text-[11px] font-mono break-all select-all">{{ host_url }}playlist.m3u</p>
        </div>
    </div>
</body>
</html>
"""

# --- 4. المسارات (Routes) ---

@app.route('/admin')
def admin():
    if request.args.get('pw') != ADMIN_PASSWORD:
        return "Access Denied", 403
    ads = list(ads_col.find()) if ads_col is not None else []
    sources = list(sources_col.find()) if sources_col is not None else []
    return render_template_string(HTML_TEMPLATE, ads=ads, sources=sources, host_url=request.host_url)

@app.route('/admin/add_ad', methods=['POST'])
def add_ad():
    if ads_col is not None:
        ads_col.insert_one({
            "name": request.form['name'],
            "url": request.form['url'],
            "logo": "https://cdn-icons-png.flaticon.com/512/743/743224.png",
            "clicks": 0
        })
    return redirect(f'/admin?pw={ADMIN_PASSWORD}')

@app.route('/admin/delete_ad/<id>')
def delete_ad(id):
    if ads_col is not None:
        ads_col.delete_one({"_id": ObjectId(id)})
    return redirect(f'/admin?pw={ADMIN_PASSWORD}')

@app.route('/admin/add_source', methods=['POST'])
def add_source():
    if sources_col is not None:
        sources_col.insert_one({"url": request.form['url'].strip()})
    return redirect(f'/admin?pw={ADMIN_PASSWORD}')

# --- المسار الرئيسي لإنشاء القائمة وحقن الإعلانات ---
@app.route('/playlist.m3u')
def get_playlist():
    def generate():
        yield "#EXTM3U\n"
        
        # قناة فحص للتأكد من أن السيرفر يعمل
        yield '#EXTINF:-1 tvg-logo="https://cdn-icons-png.flaticon.com/512/190/190411.png", [✅ سيرفرك يعمل بنجاح]\n'
        yield 'http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4\n'

        # 1. حقن الإعلانات من MongoDB في أعلى القائمة
        if ads_col is not None:
            for ad in ads_col.find():
                logo = ad.get("logo", "https://cdn-icons-png.flaticon.com/512/743/743224.png")
                yield f'#EXTINF:-1 tvg-logo="{logo}", {ad["name"]}\n'
                # تحويل الضغطة إلى مسار /go لتسجيل النقرة
                yield f'{request.host_url.rstrip("/")}/go/{ad["_id"]}\n'
        
        # 2. جلب ودمج القنوات من جميع المصادر الأصلية (Streaming)
        if sources_col is not None:
            for src in sources_col.find():
                for line in stream_m3u_source(src['url']):
                    yield line

    # استخدام Mimetype متوافق جداً مع تطبيقات أندرويد IPTV
    return Response(generate(), mimetype='audio/x-mpegurl')

# مسار توجيه النقرات وحساب الإحصائيات
@app.route('/go/<id>')
def go_to_ad(id):
    if ads_col is not None:
        ad = ads_col.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$inc": {"clicks": 1}}
        )
        if ad:
            return redirect(ad['url'])
    return "Not Found", 404

if __name__ == '__main__':
    # الحصول على المنفذ من ريندر أو استخدام 10000 افتراضياً
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
