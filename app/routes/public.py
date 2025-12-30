import os
from flask import Blueprint, render_template, request, redirect
from pymongo import MongoClient
from app.utils.helpers import is_bot, get_laundry_html
from datetime import datetime

public_bp = Blueprint('public', __name__)

# --- إعداد اتصال قاعدة البيانات (محمي من الأخطاء) ---
def get_db():
    try:
        raw_uri = os.environ.get('MONGO_URI', '').strip()
        if not raw_uri: return None
        client = MongoClient(raw_uri)
        return client['elite_saas_v1']
    except:
        return None

# 1. الصفحة الرئيسية (واجهة الشركة)
@public_bp.route('/')
def home():
    return render_template('home_corporate.html')

# 2. صفحة عرض المقال (المجلة)
@public_bp.route('/<category>/<slug>')
def article_view(category, slug):
    try:
        db = get_db()
        
        # التأكد من سلامة الاتصال
        if db is None: 
            return "System Maintenance: Database Connection Pending", 500

        # أ. البحث عن الرابط
        link = db.links.find_one({"slug": slug})
        
        # ب. إذا الرابط غير موجود
        if link is None:
            return "404 - Link Not Found", 404

        # ج. كشف البوتات (حماية من الحظر)
        user_agent = request.headers.get('User-Agent', '')
        if is_bot(user_agent):
            return f"<h1>News: {link.get('title', 'Article')}</h1><p>Loading...</p>"

        # د. جلب إعدادات الكوكيز (الخاصة بالأدمن)
        settings = db.settings.find_one({"type": "global"})
        if settings is None:
            cookie_url = ""
        else:
            cookie_url = settings.get('stuffing_url', '')

        # هـ. عرض المجلة (مع تمرير الرابط الأصلي للزر)
        return render_template(
            'article_magazine.html',
            title=link.get('title', 'Breaking News'),
            category=category.upper(),
            date=datetime.utcnow().strftime('%B %d, %Y'),
            target_url=link.get('target_url', '#'),
            cookie_url=cookie_url
        )
    except Exception as e:
        return f"App Error: {str(e)}", 500

# 3. الغسالة (الوضع الشبح - Invisible Mode)
@public_bp.route('/redirect')
def redirect_engine():
    # استلام رابط الهدف من الزر
    url = request.args.get('url')
    
    # حماية أساسية
    if not url: return redirect('/')
    
    # --- التعديل الجذري: الوضع الشفاف ---
    # لا نقوم بحقن أي UTM هنا.
    # نترك الرابط كما وضعه العميل بالضبط.
    # مهمتنا فقط هي "مسح المصدر" (Referrer Killing).
    
    return get_laundry_html(url)
