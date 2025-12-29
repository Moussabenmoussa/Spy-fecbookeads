from flask import Blueprint, request, redirect, render_template
from app.utils.helpers import is_bot, get_laundry_html
from datetime import datetime

public_bp = Blueprint('public', __name__)

# 1. الصفحة الرئيسية (الشركة)
@public_bp.route('/')
def home():
    return render_template('home_corporate.html')

# 2. صفحة عرض المقال (المجلة)
# مثال الرابط: domain.com/finance/best-gold-stocks?url=TARGET_URL
@public_bp.route('/<category>/<slug>')
def article_view(category, slug):
    target_url = request.args.get('url')
    
    # إذا لم يكن هناك رابط هدف، نوجهه للرئيسية
    if not target_url: return redirect('/')

    # كشف البوتات (للحماية)
    if is_bot(request.headers.get('User-Agent', '')):
        return "<h1>Loading...</h1>"

    # إعدادات وهمية للكوكيز (سنربطها بقاعدة البيانات لاحقاً)
    # حالياً ضع رابط الأفيليت الخاص بك هنا يدوياً ليعمل فوراً
    MY_COOKIE_URL = "https://aliexpress.com" 

    return render_template(
        'article_magazine.html',
        title=slug.replace('-', ' ').title(),
        category=category.upper(),
        date=datetime.utcnow().strftime('%B %d, %Y'),
        target_url=target_url,
        cookie_url=MY_COOKIE_URL
    )

# 3. الغسالة (نفس الكود الذهبي)
@public_bp.route('/redirect')
def redirect_engine():
    url = request.args.get('url')
    traffic_type = request.args.get('type')
    
    if not url: return redirect('/')
    
    if "aliexpress.com" in url or traffic_type == "organic":
        if "utm_source" not in url:
            sep = "&" if "?" in url else "?"
            url += f"{sep}utm_source=google&utm_medium=organic&utm_campaign=search_result"
            
    return get_laundry_html(url)
