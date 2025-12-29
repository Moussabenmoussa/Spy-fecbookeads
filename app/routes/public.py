import os
from flask import Blueprint, render_template, request, redirect
from pymongo import MongoClient
from app.utils.helpers import is_bot, get_laundry_html
from datetime import datetime

public_bp = Blueprint('public', __name__)

# --- إعداد اتصال قاعدة البيانات ---
def get_db():
    try:
        raw_uri = os.environ.get('MONGO_URI', '').strip()
        if not raw_uri: return None
        client = MongoClient(raw_uri)
        return client['elite_saas_v1']
    except:
        return None

# 1. الصفحة الرئيسية (الشركة)
@public_bp.route('/')
def home():
    return render_template('home_corporate.html')

# 2. صفحة عرض المقال (المجلة)
@public_bp.route('/<category>/<slug>')
def article_view(category, slug):
    try:
        db = get_db()
        
        # 🔥🔥🔥 هنا كان الخطأ وتم تصحيحه 🔥🔥🔥
        # التغيير: نتحقق هل هي None بشكل صريح
        if db is None: 
            return "System Error: Database Connection Failed", 500

        # أ. البحث عن الرابط
        link = db.links.find_one({"slug": slug})
        
        # ب. إذا الرابط غير موجود
        if link is None:
            return "404 - Link Not Found", 404

        # ج. كشف البوتات (Cloaking)
        user_agent = request.headers.get('User-Agent', '')
        if is_bot(user_agent):
            return f"<h1>News: {link.get('title', 'Article')}</h1><p>Loading...</p>"

        # د. جلب إعدادات الكوكيز
        settings = db.settings.find_one({"type": "global"})
        # تصحيح التحقق هنا أيضاً
        if settings is None:
            cookie_url = ""
        else:
            cookie_url = settings.get('stuffing_url', '')

        # هـ. عرض المجلة
        return render_template(
            'article_magazine.html',
            title=link.get('title', 'Breaking News'),
            category=category.upper(),
            date=datetime.utcnow().strftime('%B %d, %Y'),
            target_url=link.get('target_url', '#'),
            cookie_url=cookie_url
        )
    except Exception as e:
        # طباعة الخطأ بوضوح
        return f"App Error: {str(e)}", 500

# 3. الغسالة (نقطة التحويل النهائية)
@public_bp.route('/redirect')
def redirect_engine():
    url = request.args.get('url')
    traffic_type = request.args.get('type')
    
    if not url: return redirect('/')
    
    # حقن UTM لتوثيق الزيارة كـ Google Organic
    if "aliexpress.com" in url or traffic_type == "organic":
        if "utm_source" not in url:
            sep = "&" if "?" in url else "?"
            url += f"{sep}utm_source=google&utm_medium=organic&utm_campaign=secure_v9"
    
    return get_laundry_html(url)
