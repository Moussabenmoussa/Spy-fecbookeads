import os, re, json, random, requests, datetime
from flask import Flask, render_template_string, request, redirect, Response, make_response
from pymongo import MongoClient
from bson.objectid import ObjectId
import templates
import frontend

app = Flask(__name__)

# --- إعدادات النظام وقواعد البيانات ---
raw_uri = os.getenv("MONGO_URI", "").strip()
MONGO_URI = re.sub(r'[\s\n\r]', '', raw_uri)
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "himsounin1$")

client = MongoClient(MONGO_URI)
db = client['elite_system_v10'] # تحديث اسم القاعدة للنسخة الجديدة
links_col = db['links']
settings_col = db['settings']
articles_col = db['articles']
public_logs = db['public_logs']

# عناكب البحث للأرشفة الفورية
SEARCH_ENGINES_PING = [
    "http://www.google.com/ping?sitemap={host}sitemap.xml",
    "http://www.bing.com/ping?sitemap={host}sitemap.xml"
]

# مقالات الطوارئ (في حال كانت القاعدة فارغة)
DEFAULT_ARTICLES = [
    {
        "title": "Cloud Distribution and Protocol Integrity",
        "body": "<p>Ensuring the integrity of digital distribution networks requires a robust understanding of cloud-native architectures.</p>",
        "category": "tech",
        "meta_desc": "Analysis of cloud protocols and integrity standards.",
        "image": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=800",
        "created_at": datetime.datetime.utcnow()
    }
]

def get_settings():
    s = settings_col.find_one({"type": "global"})
    if not s:
        default = {"type": "global", "stuffing_url": "", "exit_url": ""}
        settings_col.insert_one(default)
        return default
    return s

def get_client_ip():
    if request.headers.getlist("X-Forwarded-For"):
        return request.headers.getlist("X-Forwarded-For")[0]
    return request.remote_addr

# --- ⚡ محرك السيو التلقائي (Auto-SEO Engine) ---
def extract_seo_data(html_content):
    seo_data = {"description": "", "image": ""}
    p_match = re.search(r'<p[^>]*>(.*?)</p>', html_content, re.IGNORECASE | re.DOTALL)
    if p_match:
        clean_text = re.sub(r'<.*?>', '', p_match.group(1))
        seo_data["description"] = clean_text[:160] + "..." if len(clean_text) > 160 else clean_text
    img_match = re.search(r'<img[^>]+src="([^">]+)"', html_content, re.IGNORECASE)
    if img_match:
        seo_data["image"] = img_match.group(1)
    return seo_data

def ping_engines(host_url):
    for engine in SEARCH_ENGINES_PING:
        try: requests.get(engine.format(host=host_url), timeout=2)
        except: pass

# --- ✅ 1. الصفحة الرئيسية (المجلة الحقيقية Dynamic Magazine) ---
@app.route('/', methods=['GET'])
def home():
    # 1. فلترة حسب القسم (Category)
    category_filter = request.args.get('category')
    query = {"category": category_filter} if category_filter else {}
    
    # 2. جلب المقالات الحقيقية من القاعدة (أحدث 12 مقال)
    articles_cursor = articles_col.find(query).sort("created_at", -1).limit(12)
    articles = list(articles_cursor)
    
    # 3. جلب قائمة الأقسام للقائمة العلوية
    niches = articles_col.distinct("category")
    clean_niches = [n for n in niches if n and n.strip()]
    
    return render_template_string(
        frontend.HOME_HTML, 
        articles=articles,       # نمرر المقالات الحقيقية
        niches=clean_niches,     # نمرر الأقسام
        active_category=category_filter
    )

# --- ✅ 2. قارئ المقالات العضوي (Organic Reader) ---
# هذا المسار مخصص للزوار القادمين من الصفحة الرئيسية (لإثبات المصداقية)
@app.route('/read/<id>')
def read_article(id):
    try:
        art = articles_col.find_one({"_id": ObjectId(id)})
        if not art: return redirect('/')
        
        s = get_settings()
        
        return render_template_string(
            templates.LANDING_HTML,
            target_url=s['exit_url'], # هدف افتراضي
            s=s,
            article=art,
            slug=None, # لا يوجد Slug رابط لأنها قراءة عضوية
            category=art.get('category', 'General'),
            related_posts=[]
        )
    except: return redirect('/')

# --- ✅ 3. بوابة العرض الذكية (Affiliate Gateway) ---
@app.route('/v/<slug>')
@app.route('/<category>/<slug>')
def gateway(slug, category=None):
    ua = request.headers.get('User-Agent', '').lower()
    
    link = links_col.find_one({"slug": slug})
    if not link: return "404 - Article Not Found", 404

    # المنطق السياقي (Contextual Logic)
    final_article = None
    link_tag = link.get('tag', '').strip().lower()
    
    if link_tag:
        matched = list(articles_col.aggregate([{"$match": {"category": link_tag}}, {"$sample": {"size": 1}}]))
        if matched: final_article = matched[0]

    if not final_article:
        random_art = list(articles_col.aggregate([{"$sample": {"size": 1}}]))
        if random_art: final_article = random_art[0]
    
    if not final_article: final_article = random.choice(DEFAULT_ARTICLES)

    # تحسينات النخبة (Elite Opts)
    if 'body' in final_article:
        final_article['body'] = final_article['body'].replace('<img ', '<img loading="lazy" ')

    # جلب مقالات ذات صلة للتشبيك الداخلي
    related_posts = []
    if link_tag:
        related_posts = list(links_col.find({"tag": link_tag, "slug": {"$ne": slug}}).limit(3))

    # الكلوكينج (Cloaking)
    if any(bot in ua for bot in ["google", "facebook", "bing", "bot", "crawler"]):
        return f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>{final_article['title']}</title><meta name="description" content="{final_article.get('meta_desc', '')}"></head><body><h1>{final_article['title']}</h1>{final_article.get('body', '')}</body></html>"""
    
    links_col.update_one({"slug": slug}, {"$inc": {"clicks": 1}})
    
    return render_template_string(
        templates.LANDING_HTML, 
        target_url=link['target_url'], 
        s=get_settings(), 
        article=final_article, 
        slug=slug,
        related_posts=related_posts,
        category=link_tag
    )

# --- خريطة الموقع ---
@app.route('/sitemap.xml')
def sitemap():
    links = list(links_col.find())
    base_url = request.host_url.rstrip('/')
    xml = ['<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for link in links:
        tag = link.get('tag', 'v')
        url = f"{base_url}/{tag}/{link['slug']}"
        xml.append(f'<url><loc>{url}</loc><lastmod>{datetime.datetime.now().strftime("%Y-%m-%d")}</lastmod></url>')
    xml.append('</urlset>')
    return Response(''.join(xml), mimetype='application/xml')

# --- الروابط العامة ---
@app.route('/public/shorten', methods=['POST'])
def public_shorten():
    target = request.form.get('target_url')
    cat = request.form.get('category', 'general')
    ip = get_client_ip(); today = datetime.datetime.utcnow().strftime('%Y-%m-%d')
    
    if request.cookies.get('traficoon_limit') == today or public_logs.find_one({"ip": ip, "date": today}):
        return "<h3>Limit Exceeded</h3>", 429

    slug = re.sub(r'[^a-z0-9]', '', cat.lower()) + "-" + os.urandom(3).hex()
    links_col.insert_one({"title": f"Public - {cat}", "target_url": target, "slug": slug, "clicks": 0, "tag": cat, "is_public": True, "created_at": datetime.datetime.utcnow()})
    public_logs.insert_one({"ip": ip, "date": today})
    
    final = f"{request.host_url}{cat}/{slug}"
    resp = make_response(f"<div style='text-align:center;padding:50px;'><h1>Done!</h1><input value='{final}' readonly></div>")
    resp.set_cookie('traficoon_limit', today, max_age=86400)
    return resp

# --- الغسالة ---
@app.route('/redirect')
def laundry():
    url = request.args.get('url'); t = request.args.get('type')
    if not url: return redirect('/')
    if "aliexpress" in url or t == "organic":
        if "utm_source" not in url: url += ("&" if "?" in url else "?") + "utm_source=google&utm_medium=organic"
    return f'<script>window.location.replace("{url}");</script>'

# --- لوحة التحكم ---
@app.route('/admin')
def admin():
    if request.args.get('pw') != ADMIN_PASSWORD: return "Denied", 403
    return render_template_string(templates.ADMIN_HTML, links=list(links_col.find().sort("_id", -1)), articles=list(articles_col.find().sort("_id", -1)), s=get_settings(), host_url=request.host_url)

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
    ping_engines(request.host_url)
    return redirect(f"/admin?pw={ADMIN_PASSWORD}")

@app.route('/admin/delete/<id>')
def delete_link(id): links_col.delete_one({"_id": ObjectId(id)}); return redirect(f"/admin?pw={ADMIN_PASSWORD}")

@app.route('/admin/delete_article/<id>')
def delete_article(id): articles_col.delete_one({"_id": ObjectId(id)}); return redirect(f"/admin?pw={ADMIN_PASSWORD}")

@app.route('/admin/update_settings', methods=['POST'])
def update_settings():
    settings_col.update_one({"type": "global"}, {"$set": {"stuffing_url": request.form['stuffing_url'], "exit_url": request.form['exit_url']}})
    return redirect(f"/admin?pw={ADMIN_PASSWORD}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
