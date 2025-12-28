import os, re, json, random, requests, datetime
from flask import Flask, render_template_string, request, redirect, Response, make_response
from pymongo import MongoClient
from bson.objectid import ObjectId
import templates
import frontend  # 🆕 استيراد ملف الواجهة الجديد

# --- مقالات الطوارئ ---
DEFAULT_ARTICLES = [
    {
        "title": "Cloud Distribution and Protocol Integrity",
        "body": "<p>Ensuring the integrity of digital distribution networks requires a robust understanding of cloud-native architectures.</p>",
        "category": "tech"
    },
    {
        "title": "Secure Resource Allocation Standards",
        "body": "<p>Zero-trust verification protocols are essential for preventing automated scraping.</p>",
        "category": "security"
    }
]

app = Flask(__name__)

# --- Database Setup ---
raw_uri = os.getenv("MONGO_URI", "").strip()
MONGO_URI = re.sub(r'[\s\n\r]', '', raw_uri)
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "himsounin1$")

client = MongoClient(MONGO_URI)
db = client['elite_system_v8']
links_col = db['links']
settings_col = db['settings']
articles_col = db['articles']
public_logs = db['public_logs'] # 🆕 سجل الروابط العامة للحماية

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

# --- 🆕 Route: الصفحة الرئيسية العامة (TRAFICOON Home) ---
@app.route('/', methods=['GET'])
def home():
    # 1. جلب النيتشات المتوفرة من قاعدة البيانات
    # نبحث عن كل التصنيفات الموجودة في المقالات ونزيل التكرار
    niches = articles_col.distinct("category")
    # تنظيف القائمة (إزالة الفراغات والقيم الفارغة)
    clean_niches = [n for n in niches if n and n.strip()]
    if not clean_niches: clean_niches = ["General", "Tech", "News"] # قيم افتراضية
    
    return render_template_string(frontend.HOME_HTML, niches=clean_niches)

# --- 🆕 Route: إنشاء رابط عام (مع حماية مشددة) ---
@app.route('/public/shorten', methods=['POST'])
def public_shorten():
    target_url = request.form.get('target_url')
    category = request.form.get('category', 'general')
    ip = get_client_ip()
    today = datetime.datetime.utcnow().strftime('%Y-%m-%d')
    
    # 🛡️ الحماية 1: فحص الكوكيز (هل أنشأ رابطاً اليوم؟)
    if request.cookies.get('traficoon_limit') == today:
        return "<h3>Rate Limit Exceeded: One link per day allowed. (Cookie)</h3>", 429

    # 🛡️ الحماية 2: فحص قاعدة البيانات (هل هذا IP أنشأ رابطاً اليوم؟)
    log_check = public_logs.find_one({"ip": ip, "date": today})
    if log_check:
        return "<h3>Rate Limit Exceeded: One link per day allowed. (IP)</h3>", 429

    # ✅ السماح بالإنشاء
    title = f"Public Link - {category.upper()}"
    slug = re.sub(r'[^a-z0-9]', '', category.lower()) + "-" + os.urandom(3).hex()
    
    links_col.insert_one({
        "title": title,
        "target_url": target_url,
        "slug": slug,
        "clicks": 0,
        "tag": category, # ربط الرابط بالنيتش المختار
        "is_public": True,
        "created_at": datetime.datetime.utcnow()
    })
    
    # تسجيل العملية للحظر المستقبلي
    public_logs.insert_one({"ip": ip, "date": today})

    # بناء الرابط النهائي
    final_link = f"{request.host_url}v/{slug}"
    
    # الرد مع زرع كوكيز الحظر
    resp = make_response(f"""
    <div style='font-family:sans-serif; text-align:center; padding:50px; background:#f0f9ff;'>
        <h1 style='color:#0369a1;'>Link Generated Successfully! ✅</h1>
        <input value='{final_link}' style='width:80%; padding:15px; font-size:18px;' readonly>
        <p style='color:#64748b; margin-top:20px;'>Category: <strong>{category}</strong></p>
        <a href='/' style='display:block; margin-top:30px;'>Back Home</a>
    </div>
    """)
    # ضبط الكوكيز لينتهي بنهاية اليوم
    resp.set_cookie('traficoon_limit', today, max_age=86400)
    return resp

# --- باقي المسارات (Gateway, Redirect, Admin) كما هي بالضبط ---
# (لم أغير فيها شيئاً، فقط نسختها لتعمل مع التحديث الجديد)

def get_wiki_content(slug):
    try:
        clean_keyword = slug.rsplit('-', 1)[0].replace('-', ' ')
        search_url = "https://en.wikipedia.org/w/api.php"
        params = {"action": "query", "list": "search", "srsearch": clean_keyword, "format": "json", "utf8": 1, "srlimit": 1}
        search_res = requests.get(search_url, params=params, timeout=2).json()
        if search_res.get('query', {}).get('search'):
            best_match_title = search_res['query']['search'][0]['title']
            summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{best_match_title}"
            summary_res = requests.get(summary_url, timeout=2).json()
            if 'extract' in summary_res:
                return {"title": summary_res['title'], "body": f"<p>{summary_res['extract']}</p>"}
    except: pass
    return None

@app.route('/v/<slug>')
def gateway(slug):
    ua = request.headers.get('User-Agent', '').lower()
    link = links_col.find_one({"slug": slug})
    if not link: return "Invalid Link", 404

    final_article = None
    link_tag = link.get('tag', '').strip().lower()

    if link_tag:
        matched_articles = list(articles_col.aggregate([{"$match": {"category": link_tag}}, {"$sample": {"size": 1}}]))
        if matched_articles: final_article = matched_articles[0]

    if not final_article:
        db_articles = list(articles_col.aggregate([{"$sample": {"size": 1}}]))
        if db_articles: final_article = db_articles[0]
    
    if not final_article: final_article = get_wiki_content(slug)
    if not final_article: final_article = random.choice(DEFAULT_ARTICLES)

    if any(bot in ua for bot in ["google", "facebook", "bing", "bot", "crawler"]):
        return f"<h1>{final_article['title']}</h1><div>{final_article.get('body', '')}</div>"
    
    links_col.update_one({"slug": slug}, {"$inc": {"clicks": 1}})
    
    return render_template_string(templates.LANDING_HTML, target_url=link['target_url'], s=get_settings(), article=final_article, slug=slug)

@app.route('/redirect')
def laundry():
    url = request.args.get('url')
    traffic_type = request.args.get('type') 
    if not url: return redirect('/')
    if "aliexpress.com" in url or traffic_type == "organic":
        if "utm_source" not in url:
            separator = "&" if "?" in url else "?"
            url += f"{separator}utm_source=google&utm_medium=organic&utm_campaign=search_result"
    return f'''<html><head><meta name="referrer" content="no-referrer"><script>window.location.replace("{url}");</script></head><body style="background:#fff;"></body></html>'''

@app.route('/admin')
def admin():
    if request.args.get('pw') != ADMIN_PASSWORD: return "Denied", 403
    links = list(links_col.find().sort("_id", -1))
    articles = list(articles_col.find().sort("_id", -1))
    return render_template_string(templates.ADMIN_HTML, links=links, articles=articles, s=get_settings(), host_url=request.host_url)

# أوامر الأدمن
@app.route('/admin/create_link', methods=['POST'])
def create_link():
    title = request.form['title']
    target = request.form['target_url']
    tag = request.form.get('tag', '').strip().lower()
    slug = re.sub(r'[^a-z0-9]', '-', title.lower()).strip('-') + "-" + os.urandom(2).hex()
    links_col.insert_one({"title": title, "target_url": target, "slug": slug, "clicks": 0, "tag": tag, "is_public": False})
    return redirect(f"/admin?pw={ADMIN_PASSWORD}")

@app.route('/admin/delete/<id>')
def delete_link(id):
    links_col.delete_one({"_id": ObjectId(id)})
    return redirect(f"/admin?pw={ADMIN_PASSWORD}")

@app.route('/admin/add_article', methods=['POST'])
def add_article():
    title = request.form['title']
    html_content = request.form['html_content']
    category = request.form.get('category', '').strip().lower()
    articles_col.insert_one({"title": title, "body": html_content, "category": category})
    return redirect(f"/admin?pw={ADMIN_PASSWORD}")

@app.route('/admin/delete_article/<id>')
def delete_article(id):
    articles_col.delete_one({"_id": ObjectId(id)})
    return redirect(f"/admin?pw={ADMIN_PASSWORD}")

@app.route('/admin/update_settings', methods=['POST'])
def update_settings():
    settings_col.update_one({"type": "global"}, {"$set": {"stuffing_url": request.form['stuffing_url'], "exit_url": request.form['exit_url']}})
    return redirect(f"/admin?pw={ADMIN_PASSWORD}")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
