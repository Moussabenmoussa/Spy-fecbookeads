import os, re, json, random, requests, datetime
from flask import Flask, render_template_string, request, redirect, Response, make_response
from pymongo import MongoClient
from bson.objectid import ObjectId
import templates
import frontend

# --- Elite Configuration ---
app = Flask(__name__)
SEARCH_ENGINES_PING = [
    "http://www.google.com/ping?sitemap={host}sitemap.xml",
    "http://www.bing.com/ping?sitemap={host}sitemap.xml"
]

# --- مقالات الطوارئ (Emergency Fallback) ---
DEFAULT_ARTICLES = [
    {
        "title": "Cloud Distribution and Protocol Integrity",
        "body": "<p>Ensuring the integrity of digital distribution networks requires a robust understanding of cloud-native architectures.</p>",
        "category": "tech",
        "meta_desc": "Analysis of cloud protocols and integrity standards.",
        "image": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=800"
    }
]

# --- إعدادات قاعدة البيانات ---
raw_uri = os.getenv("MONGO_URI", "").strip()
MONGO_URI = re.sub(r'[\s\n\r]', '', raw_uri)
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "himsounin1$")

client = MongoClient(MONGO_URI)
db = client['elite_system_v8']
links_col = db['links']
settings_col = db['settings']
articles_col = db['articles']
public_logs = db['public_logs']

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
    """
    يقوم بتحليل الـ HTML لاستخراج بيانات السيو تلقائياً
    """
    seo_data = {"description": "", "image": ""}
    
    # 1. استخراج الوصف (أول فقرة نصية)
    p_match = re.search(r'<p[^>]*>(.*?)</p>', html_content, re.IGNORECASE | re.DOTALL)
    if p_match:
        # تنظيف النص من التاغات
        clean_text = re.sub(r'<.*?>', '', p_match.group(1))
        seo_data["description"] = clean_text[:160] + "..." if len(clean_text) > 160 else clean_text
    
    # 2. استخراج الصورة (أول صورة في المقال)
    img_match = re.search(r'<img[^>]+src="([^">]+)"', html_content, re.IGNORECASE)
    if img_match:
        seo_data["image"] = img_match.group(1)
        
    return seo_data

def ping_engines(host_url):
    """ استدعاء عناكب البحث (RPC Ping) """
    for engine in SEARCH_ENGINES_PING:
        try:
            requests.get(engine.format(host=host_url), timeout=2)
        except: pass

# --- ✅ 1. المسار الرئيسي (الواجهة) ---
@app.route('/', methods=['GET'])
def home():
    niches = articles_col.distinct("category")
    clean_niches = [n for n in niches if n and n.strip()]
    if not clean_niches: clean_niches = ["General", "Tech", "News"]
    return render_template_string(frontend.HOME_HTML, niches=clean_niches)

# --- ✅ 2. خريطة الموقع الديناميكية (Dynamic Sitemap) ---
@app.route('/sitemap.xml', methods=['GET'])
def sitemap():
    """ يولد خريطة XML تحتوي على كل الروابط النشطة للأرشفة الفورية """
    links = list(links_col.find())
    base_url = request.host_url.rstrip('/')
    
    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    
    for link in links:
        # استخدام الهيكلية الجديدة إذا توفر التصنيف
        if link.get('tag'):
            url = f"{base_url}/{link['tag']}/{link['slug']}"
        else:
            url = f"{base_url}/v/{link['slug']}"
            
        last_mod = datetime.datetime.now().strftime('%Y-%m-%d')
        xml.append(f'<url><loc>{url}</loc><lastmod>{last_mod}</lastmod><changefreq>daily</changefreq><priority>0.8</priority></url>')
    
    xml.append('</urlset>')
    return Response('\n'.join(xml), mimetype='application/xml')

# --- ✅ 3. إنشاء الروابط العامة ---
@app.route('/public/shorten', methods=['POST'])
def public_shorten():
    target_url = request.form.get('target_url')
    category = request.form.get('category', 'general')
    ip = get_client_ip()
    today = datetime.datetime.utcnow().strftime('%Y-%m-%d')
    
    if request.cookies.get('traficoon_limit') == today:
        return "<h3>Rate Limit Exceeded.</h3>", 429
    if public_logs.find_one({"ip": ip, "date": today}):
        return "<h3>Rate Limit Exceeded.</h3>", 429

    slug = re.sub(r'[^a-z0-9]', '', category.lower()) + "-" + os.urandom(3).hex()
    
    links_col.insert_one({
        "title": f"Public - {category}",
        "target_url": target_url,
        "slug": slug,
        "clicks": 0,
        "tag": category,
        "is_public": True,
        "created_at": datetime.datetime.utcnow()
    })
    
    public_logs.insert_one({"ip": ip, "date": today})
    
    # عرض الرابط بالهيكلية الجديدة
    final_link = f"{request.host_url}{category}/{slug}"
    
    resp = make_response(f"""
    <div style='font-family:sans-serif; text-align:center; padding:50px; background:#f0f9ff;'>
        <h1 style='color:#0369a1;'>Link Active ✅</h1>
        <input value='{final_link}' style='width:80%; padding:15px; font-size:18px;' readonly>
        <p><a href='/'>Back Home</a></p>
    </div>
    """)
    resp.set_cookie('traficoon_limit', today, max_age=86400)
    return resp

# --- ✅ 4. بوابة العرض الذكية (Smart Gateway) ---
# تدعم المسار القديم (/v/) والمسار الجديد (/category/slug)
@app.route('/v/<slug>')
@app.route('/<category>/<slug>')
def gateway(slug, category=None):
    ua = request.headers.get('User-Agent', '').lower()
    
    # البحث عن الرابط
    link = links_col.find_one({"slug": slug})
    if not link: return "404 - Article Not Found", 404

    # تحديد المقال المناسب (Contextual Logic)
    final_article = None
    link_tag = link.get('tag', '').strip().lower()
    
    # محاولة جلب مقال من نفس التصنيف
    if link_tag:
        matched = list(articles_col.aggregate([
            {"$match": {"category": link_tag}},
            {"$sample": {"size": 1}}
        ]))
        if matched: final_article = matched[0]

    # إذا لم نجد، مقال عشوائي
    if not final_article:
        random_art = list(articles_col.aggregate([{"$sample": {"size": 1}}]))
        if random_art: final_article = random_art[0]
    
    # Fallback للطوارئ
    if not final_article: final_article = random.choice(DEFAULT_ARTICLES)

    # ⚡ تحسينات النخبة (Elite Optimization) ⚡
    
    # 1. Lazy Loading Injection
    if 'body' in final_article:
        final_article['body'] = final_article['body'].replace('<img ', '<img loading="lazy" ')

    # 2. Related Articles (Internal Linking Mesh)
    related_posts = []
    if link_tag:
        related_posts = list(links_col.find(
            {"tag": link_tag, "slug": {"$ne": slug}}
        ).limit(3))

    # 3. Cloaking للبوتات
    if any(bot in ua for bot in ["google", "facebook", "bing", "bot", "crawler"]):
        # عرض نسخة نظيفة جداً للبوت
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>{final_article['title']}</title>
            <meta name="description" content="{final_article.get('meta_desc', '')}">
            <meta property="og:image" content="{final_article.get('image', '')}">
        </head>
        <body>
            <h1>{final_article['title']}</h1>
            {final_article['body']}
        </body>
        </html>
        """
    
    links_col.update_one({"slug": slug}, {"$inc": {"clicks": 1}})
    
    # إرسال البيانات للقالب الجديد
    return render_template_string(
        templates.LANDING_HTML, 
        target_url=link['target_url'], 
        s=get_settings(), 
        article=final_article, 
        slug=slug,
        related_posts=related_posts, # للتشبيك الداخلي
        category=link_tag
    )

# --- غسالة الروابط ---
@app.route('/redirect')
def laundry():
    url = request.args.get('url')
    traffic_type = request.args.get('type') 
    if not url: return redirect('/')
    
    # Organic Injection
    if "aliexpress.com" in url or traffic_type == "organic":
        if "utm_source" not in url:
            sep = "&" if "?" in url else "?"
            url += f"{sep}utm_source=google&utm_medium=organic&utm_campaign=search_result"
            
    # Double-Meta Refresh (Clean Referrer)
    return f'''<html><head><meta name="referrer" content="no-referrer"><script>window.location.replace("{url}");</script></head><body></body></html>'''

# --- لوحة التحكم ---
@app.route('/admin')
def admin():
    if request.args.get('pw') != ADMIN_PASSWORD: return "Denied", 403
    links = list(links_col.find().sort("_id", -1))
    articles = list(articles_col.find().sort("_id", -1))
    return render_template_string(templates.ADMIN_HTML, links=links, articles=articles, s=get_settings(), host_url=request.host_url)

@app.route('/admin/create_link', methods=['POST'])
def create_link():
    title = request.form['title']
    target = request.form['target_url']
    tag = request.form.get('tag', 'general').strip().lower()
    
    # Slug نظيف للسيو
    clean_slug = re.sub(r'[^a-z0-9]', '-', title.lower()).strip('-')
    slug = f"{clean_slug}-{os.urandom(2).hex()}"
    
    links_col.insert_one({
        "title": title, 
        "target_url": target, 
        "slug": slug, 
        "clicks": 0, 
        "tag": tag, 
        "is_public": False
    })
    return redirect(f"/admin?pw={ADMIN_PASSWORD}")

@app.route('/admin/delete/<id>')
def delete_link(id):
    links_col.delete_one({"_id": ObjectId(id)})
    return redirect(f"/admin?pw={ADMIN_PASSWORD}")

@app.route('/admin/add_article', methods=['POST'])
def add_article():
    title = request.form['title']
    html_content = request.form['html_content']
    category = request.form.get('category', 'general').strip().lower()
    
    # ⚡ استخراج بيانات السيو تلقائياً
    seo_info = extract_seo_data(html_content)
    
    articles_col.insert_one({
        "title": title, 
        "body": html_content, 
        "category": category,
        "meta_desc": seo_info['description'],
        "image": seo_info['image'],
        "created_at": datetime.datetime.utcnow()
    })
    
    # ⚡ RPC Ping (استدعاء جوجل)
    ping_engines(request.host_url)
    
    return redirect(f"/admin?pw={ADMIN_PASSWORD}")

@app.route('/admin/delete_article/<id>')
def delete_article(id):
    articles_col.delete_one({"_id": ObjectId(id)})
    return redirect(f"/admin?pw={ADMIN_PASSWORD}")

@app.route('/admin/update_settings', methods=['POST'])
def update_settings():
    settings_col.update_one({"type": "global"}, {"$set": {
        "stuffing_url": request.form['stuffing_url'], 
        "exit_url": request.form['exit_url']
    }})
    return redirect(f"/admin?pw={ADMIN_PASSWORD}")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
