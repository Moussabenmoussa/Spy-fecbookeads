import os, re, json, random, requests, datetime, html
from flask import Flask, render_template_string, request, redirect, Response, make_response, session, url_for, flash
from pymongo import MongoClient
from bson.objectid import ObjectId
from urllib.parse import urlparse
import templates
import frontend

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key_847382')

# --- Database Connection ---
MONGO_URI = os.environ.get('MONGO_URI')
client = MongoClient(MONGO_URI)
db = client.get_database()
articles_collection = db['articles']

# --- High CPC Configuration (The Elite List) ---
# 1. قائمة الكلمات الأغلى سعراً (High CPC Keywords)
HIGH_CPC_HASHES = [
    "insurance-claim-quote-auto",
    "mesothelioma-lawyer-attorney-california",
    "structured-settlement-annuity-companies",
    "business-voip-phone-services-cloud",
    "online-degree-education-mba-programs",
    "donate-car-to-charity-california"
]

# 2. خريطة السياق الذكية (لربط المحتوى بالهاش)
HASH_MAP = {
    r"insurance|claim|auto": "insurance-claim-quote-auto",
    r"lawyer|attorney|legal": "mesothelioma-lawyer-attorney-california",
    r"settlement|annuity": "structured-settlement-annuity-companies",
    r"voip|cloud|phone": "business-voip-phone-services-cloud",
    r"mba|degree|education": "online-degree-education-mba-programs",
    r"donate|car|charity": "donate-car-to-charity-california"
}

# --- Helper Functions ---
def is_safe_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return parsed.scheme in ["http", "https"] and bool(parsed.netloc)
    except:
        return False

def match_contextual_hash(url: str) -> str:
    for pattern, hash_val in HASH_MAP.items():
        if re.search(pattern, url, re.IGNORECASE):
            return hash_val
    return random.choice(HIGH_CPC_HASHES)

# --- Routes ---

@app.route('/')
def home():
    category = request.args.get('category')
    page = int(request.args.get('page', 1))
    limit = 6  # عدد المقالات في الصفحة
    
    query = {}
    if category:
        query['category'] = category
    
    # جلب المقالات مرتبة بالأحدث
    total_articles = articles_collection.count_documents(query)
    articles_cursor = articles_collection.find(query).sort('_id', -1).skip((page-1)*limit).limit(limit)
    articles = list(articles_cursor)
    
    # تحويل ObjectId إلى نص
    for art in articles:
        art['_id'] = str(art['_id'])
        # استخراج صورة افتراضية إذا لم توجد
        if 'image' not in art:
            art['image'] = 'https://via.placeholder.com/800x600?text=No+Image'

    # تحديد النيتشات للقائمة
    niches = articles_collection.distinct('category')
    
    # حساب هل توجد صفحات أخرى
    has_next = (page * limit) < total_articles
    
    # إذا كان الطلب AJAX (لزر Load More)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template_string(frontend.ARTICLES_GRID_HTML, articles=articles)

    return render_template_string(frontend.HOME_HTML, articles=articles, niches=niches, current_category=category, has_next=has_next, page=page)

@app.route('/p/<slug>')
def article_page(slug):
    # البحث عن المقال (يمكن تطويره لاستخدام slug فعلي، هنا نستخدم ID أو Title للتبسيط، سأفترض أنك تستخدم ID في الرابط حالياً)
    # ملاحظة: لتحسين SEO يفضل استخدام Slug، لكن للكود الحالي سنبحث بالـ ID إذا كان الرابط p/ID
    try:
        article = articles_collection.find_one({'_id': ObjectId(slug)})
    except:
        article = None
        
    if not article:
        return "Article not found", 404
        
    article['_id'] = str(article['_id'])
    
    # جلب مقالات ذات صلة (نفس التصنيف)
    related = list(articles_collection.find({'category': article['category'], '_id': {'$ne': ObjectId(slug)}}).limit(3))
    for r in related: r['_id'] = str(r['_id'])

    return render_template_string(frontend.ARTICLE_HTML, article=article, related=related)

# --- الغسالة المطورة (V4: Anchor Click Simulation) ---
@app.route('/redirect')
def laundry():
    url = request.args.get('url')

    if not url or not is_safe_url(url):
        return "Invalid Request", 400

    # 1. استراتيجية UTM (Time-Based)
    if "utm_source" not in url:
        hour = datetime.datetime.utcnow().hour
        campaign_time = "morning" if 6 <= hour < 12 else "evening" if 18 <= hour < 24 else "daytime"
        separator = "&" if "?" in url else "?"
        url += f"{separator}utm_source=google&utm_medium=organic&utm_campaign={campaign_time}"

    # 2. حقن الهاش السياقي (Contextual Hash)
    if "#" not in url:
        fake_context = match_contextual_hash(url)
        url += f"#{fake_context}"

    safe_url_html = html.escape(url, quote=True)
    
    messages = [
        "Redirecting you securely...",
        "Establishing secure connection...",
        "Loading destination...",
        "Please wait, verifying link...",
        "Processing request..."
    ]
    message = random.choice(messages)

    # 3. الصفحة النهائية (تستخدم محاكاة الضغط + Rel Noreferrer)
    html_page = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="referrer" content="no-referrer">
        <title>{message}</title>
        <style>
            body{{font-family:-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; display:flex; flex-direction:column; justify-content:center; align-items:center; height:100vh; margin:0; background:#f8fafc; color:#64748b; font-size:14px;}}
            .spinner {{width: 40px; height: 40px; border: 4px solid #e2e8f0; border-top: 4px solid #3b82f6; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 20px;}}
            @keyframes spin {{0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }}}}
        </style>
    </head>
    <body>
        <div class="spinner"></div>
        <p><b>Secure Gateway:</b> {message}</p>
        
        <a id="secure-link" href="{safe_url_html}" rel="noreferrer" style="display:none;"></a>

        <script>
            // محاكاة ضغطة الزر بعد 1.5 ثانية
            setTimeout(function() {{
                document.getElementById('secure-link').click();
            }}, 1500); 
        </script>

        <noscript>
            <a href="{safe_url_html}" rel="noreferrer">Click here to continue</a>
        </noscript>
    </body>
    </html>
    """

    # الحماية الثلاثية (Header + Meta + Rel)
    response = make_response(html_page)
    response.headers['Referrer-Policy'] = 'no-referrer'
    return response

# --- Admin Panel ---
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == "123456": # غير كلمة السر لاحقاً
            session['admin_logged_in'] = True
            return redirect('/admin/dashboard')
        else:
            return "Wrong Password!"
    return templates.LOGIN_HTML

@app.route('/admin/dashboard', methods=['GET', 'POST'])
def dashboard():
    if not session.get('admin_logged_in'):
        return redirect('/admin')
    
    if request.method == 'POST':
        # إضافة مقال جديد
        title = request.form.get('title')
        category = request.form.get('category').lower()
        content = request.form.get('content') # HTML Content
        
        # استخراج الصورة تلقائياً من المحتوى
        image = ""
        img_match = re.search(r'src="([^"]+)"', content)
        if img_match:
            image = img_match.group(1)
        else:
            image = "https://via.placeholder.com/800x600?text=No+Image"
            
        articles_collection.insert_one({
            "title": title,
            "category": category,
            "content": content,
            "image": image,
            "date": datetime.datetime.now()
        })
        return redirect('/admin/dashboard')

    articles = list(articles_collection.find().sort('_id', -1))
    for a in articles: a['_id'] = str(a['_id'])
    
    return render_template_string(templates.DASHBOARD_HTML, articles=articles)

@app.route('/admin/delete/<id>')
def delete_article(id):
    if not session.get('admin_logged_in'): return redirect('/admin')
    articles_collection.delete_one({'_id': ObjectId(id)})
    return redirect('/admin/dashboard')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
