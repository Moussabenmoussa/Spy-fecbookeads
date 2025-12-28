import os, re, json, random, requests
from flask import Flask, render_template_string, request, redirect, Response
from pymongo import MongoClient
from bson.objectid import ObjectId
import templates

# --- مقالات الطوارئ (الخطة د: تعمل فقط إذا فشل كل شيء) ---
DEFAULT_ARTICLES = [
    {
        "title": "Cloud Distribution and Protocol Integrity",
        "body": "<p>Ensuring the integrity of digital distribution networks requires a robust understanding of cloud-native architectures. As security handshakes become more complex, systems now implement multiple layers of IP validation.</p>"
    },
    {
        "title": "Optimizing Edge Computing Networks",
        "body": "<p>The evolution of edge computing allows for faster resource delivery across decentralized nodes. By implementing advanced caching strategies, we can reduce latency significantly while maintaining secure data tunnels.</p>"
    },
    {
        "title": "Secure Resource Allocation Standards",
        "body": "<p>Zero-trust verification protocols are essential for preventing automated scraping. By validating every request through a secure gateway, systems can differentiate between legitimate human interaction and bot-driven traffic.</p>"
    }
]

app = Flask(__name__)

# --- Database & Security Configuration ---
raw_uri = os.getenv("MONGO_URI", "").strip()
MONGO_URI = re.sub(r'[\s\n\r]', '', raw_uri)
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "himsounin1$")

client = MongoClient(MONGO_URI)
db = client['elite_system_v8']
links_col = db['links']
settings_col = db['settings']
articles_col = db['articles']

def get_settings():
    s = settings_col.find_one({"type": "global"})
    if not s:
        default = {"type": "global", "stuffing_url": "", "exit_url": ""}
        settings_col.insert_one(default)
        return default
    return s

# --- دالة ويكيبيديا الذكية (الخطة ج) ---
def get_wiki_content(slug):
    try:
        clean_keyword = slug.rsplit('-', 1)[0].replace('-', ' ')
        search_url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query", "list": "search", "srsearch": clean_keyword,
            "format": "json", "utf8": 1, "srlimit": 1
        }
        search_res = requests.get(search_url, params=params, timeout=2).json()
        if search_res.get('query', {}).get('search'):
            best_match_title = search_res['query']['search'][0]['title']
            summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{best_match_title}"
            summary_res = requests.get(summary_url, timeout=2).json()
            if 'extract' in summary_res:
                return {
                    "title": summary_res['title'],
                    "body": f"<p>{summary_res['extract']}</p>"
                }
    except: pass
    return None

# --- Routes ---

@app.route('/v/<slug>')
def gateway(slug):
    ua = request.headers.get('User-Agent', '').lower()
    
    # 1. جلب الرابط أولاً لمعرفة التصنيف (Tag) الخاص به
    link = links_col.find_one({"slug": slug})
    if not link: return "Invalid Link", 404

    # --- نظام اختيار المحتوى الذكي (Contextual Engine) ---
    final_article = None
    link_tag = link.get('tag', '').strip().lower() # جلب تصنيف الرابط

    # أ. الأولوية الأولى: البحث عن مقال مطابق للتصنيف (Perfect Match)
    if link_tag:
        matched_articles = list(articles_col.aggregate([
            {"$match": {"category": link_tag}},
            {"$sample": {"size": 1}}
        ]))
        if matched_articles:
            final_article = matched_articles[0]

    # ب. الأولوية الثانية: إذا لم نجد تطابق، نأخذ أي مقال احترافي عشوائي من الأدمن
    if not final_article:
        db_articles = list(articles_col.aggregate([{"$sample": {"size": 1}}]))
        if db_articles:
            final_article = db_articles[0]
    
    # ج. الأولوية الثالثة: ويكيبيديا
    if not final_article:
        final_article = get_wiki_content(slug)
    
    # د. الأولوية الرابعة: الطوارئ
    if not final_article:
        final_article = random.choice(DEFAULT_ARTICLES)

    # --- نظام التخفي (Cloaking) ---
    if any(bot in ua for bot in ["google", "facebook", "bing", "bot", "crawler"]):
        return f"<h1>{final_article['title']}</h1><div>{final_article.get('body', '')}</div>"
    
    # تسجيل النقرة
    links_col.update_one({"slug": slug}, {"$inc": {"clicks": 1}})
    
    return render_template_string(
        templates.LANDING_HTML, 
        target_url=link['target_url'], 
        s=get_settings(), 
        article=final_article,
        slug=slug
    )

@app.route('/redirect')
def laundry():
    url = request.args.get('url')
    # نستقبل نوع الترافيك
    traffic_type = request.args.get('type') 
    
    if not url: return redirect('/')
    
    # المنطق المطور: تطبيق التمويه على علي إكسبريس وأي رابط "organic"
    if "aliexpress.com" in url or traffic_type == "organic":
        if "utm_source" not in url:
            separator = "&" if "?" in url else "?"
            url += f"{separator}utm_source=google&utm_medium=organic&utm_campaign=search_result"
    
    # صفحة الغسيل (Referrer Killing)
    return f'''
    <html>
    <head>
        <meta name="referrer" content="no-referrer">
        <script>window.location.replace("{url}");</script>
    </head>
    <body style="background:#fff;"></body>
    </html>
    '''

@app.route('/admin')
def admin():
    if request.args.get('pw') != ADMIN_PASSWORD: return "Denied", 403
    links = list(links_col.find().sort("_id", -1))
    articles = list(articles_col.find().sort("_id", -1))
    return render_template_string(templates.ADMIN_HTML, links=links, articles=articles, s=get_settings(), host_url=request.host_url)

# --- إدارة الروابط (مع التصنيف Tag) ---
@app.route('/admin/create_link', methods=['POST'])
def create_link():
    title = request.form['title']
    target = request.form['target_url']
    tag = request.form.get('tag', '').strip().lower() # استقبال التصنيف
    
    slug = re.sub(r'[^a-z0-9]', '-', title.lower()).strip('-') + "-" + os.urandom(2).hex()
    links_col.insert_one({"title": title, "target_url": target, "slug": slug, "clicks": 0, "tag": tag})
    return redirect(f"/admin?pw={ADMIN_PASSWORD}")

@app.route('/admin/delete/<id>')
def delete_link(id):
    links_col.delete_one({"_id": ObjectId(id)})
    return redirect(f"/admin?pw={ADMIN_PASSWORD}")

# --- إدارة المقالات (مع التصنيف Category) ---
@app.route('/admin/add_article', methods=['POST'])
def add_article():
    title = request.form['title']
    html_content = request.form['html_content']
    category = request.form.get('category', '').strip().lower() # استقبال التصنيف
    
    articles_col.insert_one({"title": title, "body": html_content, "category": category})
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
