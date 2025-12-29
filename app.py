import os, re, json, random, requests, datetime, html 
from flask import Flask, render_template_string, request, redirect, Response, make_response
from pymongo import MongoClient
from bson.objectid import ObjectId
from urllib.parse import urlparse
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

# 👇 دالة حقن الاقتراحات الذكية (Don't Miss) 👇
def inject_recommendation(html_content, category, current_id):
    try:
        # 1. البحث عن مقال آخر في نفس القسم (غير المقال الحالي)
        related = articles_col.find_one({
            "category": category,
            "_id": {"$ne": ObjectId(current_id)}
        })
        
        # إذا لم نجد في نفس القسم، نأتي بأي مقال آخر
        if not related:
            related = articles_col.find_one({"_id": {"$ne": ObjectId(current_id)}})

        if related:
            # 2. تصميم الصندوق الاحترافي (Professional Card)
            card = f"""
            <div style="border-left: 4px solid #2563eb; background: #f8fafc; padding: 20px; margin: 30px 0; border-radius: 0 8px 8px 0;">
                <span style="display: block; color: #64748b; font-size: 10px; font-weight: 800; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px;">Don't Miss</span>
                <a href="/read/{related['_id']}" style="color: #0f172a; font-size: 17px; font-weight: 700; text-decoration: none; line-height: 1.4;">
                    {related['title']}
                </a>
            </div>
            """
            
            # 3. عملية الحقن بعد الفقرة الثانية
            # نقسم النص عند كل قفلة فقرة </p>
            paragraphs = html_content.split('</p>')
            
            # إذا كان المقال طويلاً بما يكفي (أكثر من فقرتين)
            if len(paragraphs) > 2:
                # نلصق الصندوق بعد الفقرة الثانية (Index 1)
                paragraphs[1] += "</p>" + card
                # نعيد تجميع النص مرة أخرى
                return " ".join(paragraphs[0:2]) + " ".join(paragraphs[2:])
                
    except Exception as e:
        print(f"Injection Error: {e}")
        
    return html_content # إذا حدث خطأ نعيد النص كما هو





# --- ✅ 1. الصفحة الرئيسية (المجلة الحقيقية Dynamic Magazine) ---
@app.route('/', methods=['GET'])
def home():
    # 1. فلترة حسب القسم (Category)
    category_filter = request.args.get('category')
    query = {"category": category_filter} if category_filter else {}
    
    # 2. جلب المقالات الحقيقية من القاعدة (أحدث 12 مقال)
    articles_cursor = articles_col.find(query).sort("created_at", -1).limit(30)
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


# تفعيل الحقن للقارئ العضوي أيضاً
        art['body'] = inject_recommendation(art['body'], art.get('category'), art['_id'])

        
        
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


    # 👇 تفعيل حقن الاقتراحات (Don't Miss) 👇
    if final_article and '_id' in final_article:
        final_article['body'] = inject_recommendation(
            final_article.get('body', ''), 
            final_article.get('category', 'general'), 
            final_article['_id']
        )

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
    # تنظيف اسم القسم وجعله حروفاً صغيرة
    cat = request.form.get('category', 'general').strip().lower()
    
    ip = get_client_ip()
    today = datetime.datetime.utcnow().strftime('%Y-%m-%d')
    
    # 1. نظام الحماية (Rate Limit)
    if request.cookies.get('traficoon_limit') == today or public_logs.find_one({"ip": ip, "date": today}):
        return "<h3>Limit Exceeded: One link per day allowed.</h3>", 429

    # 2. 🔥 الحل النخبوي: البحث في قاعدة البيانات عن عناوين حقيقية لهذا القسم
    # نجلب فقط حقل "title" لتقليل الحمل على السيرفر
    # نبحث عن مقالات في نفس القسم الذي اختاره المستخدم
    db_articles = list(articles_col.find({"category": cat}, {"title": 1}).limit(50))
    
    if db_articles:
        # ✅ وجدنا مقالات! نختار عنواناً عشوائياً منها ليكون هو الرابط
        chosen_title = random.choice(db_articles)['title']
        # تحويل العنوان إلى صيغة رابط (Slug)
        slug_base = re.sub(r'[^a-z0-9]+', '-', chosen_title.lower()).strip('-')
    else:
        # ⚠️ حالة احتياطية: إذا أنشأت قسماً جديداً ولم تضع فيه مقالات بعد
        # نقوم بتوليد عنوان ذكي وتلقائي
        slug_base = f"top-{cat}-trends-review"

    # إضافة كود عشوائي قصير جداً في النهاية لضمان عدم التكرار
    slug = f"{slug_base}-{os.urandom(2).hex()}"

    # الحفظ في قاعدة البيانات
    links_col.insert_one({
        "title": f"Public - {slug_base.replace('-', ' ').title()}", 
        "target_url": target, 
        "slug": slug, 
        "clicks": 0, 
        "tag": cat, 
        "is_public": True, 
        "created_at": datetime.datetime.utcnow()
    })
    
    # تسجيل اللوج للحماية
    public_logs.insert_one({"ip": ip, "date": today})
    
    final_link = f"{request.host_url}{cat}/{slug}"
    
    # عرض النتيجة
    resp = make_response(f"""
        <div style='font-family:sans-serif; text-align:center; padding:50px; background:#f8fafc;'>
            <h1 style='color:#16a34a;'>✅ Secure Link Generated</h1>
            <p style='color:#64748b; font-size:14px;'>Optimized with High-CPC Keywords</p>
            <div style='margin-top:20px;'>
                <input value='{final_link}' style='width:100%; max-width:500px; padding:15px; border:1px solid #cbd5e1; border-radius:8px; font-family:monospace; font-size:16px; color:#0f172a;' readonly onclick="this.select();">
            </div>
            <p style='color:#94a3b8; font-size:12px; margin-top:10px;'>Category: {cat.upper()} | Base: {slug_base}</p>
            <br>
            <a href='/' style='text-decoration:none; color:#2563eb; font-weight:bold;'>Create Another</a>
        </div>
    """)
    resp.set_cookie('traficoon_limit', today, max_age=86400)
    return response
   



  





@app.route('/redirect')
def laundry():
    url = request.args.get('url')
    user_agent = request.headers.get('User-Agent', '')

    # 1. طرد البوتات
    if is_bot(user_agent):
        return redirect("/", code=302)

    if not url: return "Error", 400

    # 2. تجهيز الرابط الذهبي
    # بما أننا سنقتل المصدر 100%، يمكننا الآن استخدام utm_source=google بأمان
    # لأن الـ Referrer سيصل فارغاً (Direct)، وجوجل سيظن أن الزائر فتح الرابط من الذاكرة
    separator = "&" if "?" in url else "?"
    final_url = f"{url}{separator}utm_source=google&utm_medium=organic&utm_campaign=search_v9"
    
    # 3. صفحة الشبح (The Ghost Page)
    html_page = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Securing...</title>
        <style>
            body {{ background: #000; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; color: #fff; font-family: sans-serif; }}
            .loader {{ width: 50px; height: 50px; border: 5px solid #333; border-top: 5px solid #2563eb; border-radius: 50%; animation: spin 1s linear infinite; }}
            @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
        </style>
    </head>
    <body>
        <div class="loader"></div>
        <div style="display:none" id="dest">{final_url}</div>

        <script>
            // التقنية المحرمة: Iframe Injection
            // هذه التقنية تعزل الصفحة الحالية عن الصفحة القادمة تماماً
            
            setTimeout(function() {{
                var dest = document.getElementById('dest').innerText;
                
                // إنشاء إطار وهمي
                var iframe = document.createElement("iframe");
                iframe.style.display = "none";
                document.body.appendChild(iframe);
                
                // الكتابة داخل الإطار الوهمي (يصبح صفحة جديدة بلا تاريخ)
                var frameDoc = iframe.contentDocument || iframe.contentWindow.document;
                
                var payload = `
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <meta name="referrer" content="no-referrer">
                    </head>
                    <body>
                        <script>
                            // التحويل من داخل الإطار المعزول
                            window.parent.location.replace("` + dest + `");
                        <\/script>
                    </body>
                    </html>
                `;
                
                frameDoc.open();
                frameDoc.write(payload);
                frameDoc.close();
                
            }}, 800); // انتظار بسيط لضمان تحميل الصفحة
        </script>
    </body>
    </html>
    """
    
    response = make_response(html_page)
    # هيدرات إضافية للتأكد
    response.headers['Referrer-Policy'] = 'no-referrer'
    return response







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

# --- 🆕 إضافة: محتوى الصفحات الثابتة للمجلة (V11 Update) ---
STATIC_PAGES = {
    "about": """
        <p><strong>TRAFICOON Media Inc.</strong> is a premier digital intelligence firm established in 2023. We specialize in aggregating high-value market data across Technology, Finance, and Health sectors.</p>
        <p>Our mission is to provide actionable insights and transparent distribution protocols for the modern web. With a team of dedicated analysts and engineers, we ensure that every piece of content delivered meets the highest standards of accuracy and relevance.</p>
        <h2>Our Vision</h2>
        <p>To bridge the gap between complex market trends and everyday users through secure, simplified content delivery systems.</p>
    """,
    "privacy": """
        <p>Last Updated: December 2025</p>
        <p>At TRAFICOON, we take your privacy seriously. This Privacy Policy explains how we collect, use, and protect your information.</p>
        <h2>1. Information Collection</h2>
        <p>We collect minimal data necessary for operational purposes, including IP addresses for security verification and broad geographic analytics.</p>
        <h2>2. Cookies</h2>
        <p>We use secure cookies to enhance user experience and prevent bot activity. By using our service, you consent to our use of cookies in accordance with GDPR regulations.</p>
        <h2>3. Third-Party Disclosure</h2>
        <p>We do not sell, trade, or otherwise transfer your personally identifiable information to outside parties unless required by law.</p>
    """,
    "terms": """
        <p>By accessing TRAFICOON, you agree to be bound by these Terms of Service.</p>
        <h2>1. Use License</h2>
        <p>Permission is granted to temporarily download one copy of the materials (information or software) on TRAFICOON's website for personal, non-commercial transitory viewing only.</p>
        <h2>2. Disclaimer</h2>
        <p>The materials on TRAFICOON's website are provided on an 'as is' basis. We make no warranties, expressed or implied, and hereby disclaim and negate all other warranties including, without limitation, implied warranties of merchantability.</p>
    """,
    "contact": """
        <p>We are here to help. For general inquiries, partnership opportunities, or media requests, please reach out to our support team.</p>
        <h2>Headquarters</h2>
        <p>101 Tech Plaza, Silicon Valley, CA 94000<br>United States</p>
        <h2>Email Support</h2>
        <p><strong>General:</strong> contact@traficoon.media<br><strong>Legal:</strong> legal@traficoon.media</p>
        <p><em>Please allow up to 48 hours for a response from our team.</em></p>
    """
}

@app.route('/p/<page_name>')
def static_page(page_name):
    # تحويل الاسم لعنوان جميل (مثال: privacy -> Privacy Policy)
    titles = {"about": "About Us", "privacy": "Privacy Policy", "terms": "Terms of Service", "contact": "Contact Support"}
    content = STATIC_PAGES.get(page_name)
    
    if not content: return redirect('/')
    
    return render_template_string(frontend.PAGE_HTML, title=titles.get(page_name, page_name.title()), content=content)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
