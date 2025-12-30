from flask import Blueprint, render_template, request, redirect, session
from app import db
from datetime import datetime
import re
import os
from app.article_system import ArticleManager

dashboard_bp = Blueprint('dashboard', __name__)
article_manager = ArticleManager()

def login_required(f):
    def wrapper(*args, **kwargs):
        if 'user_email' not in session: return redirect('/login')
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

# 1. لوحة التحكم الرئيسية
@dashboard_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        target_url = request.form.get('target_url')
        category = request.form.get('category')
        title = request.form.get('title', 'Untitled')
        
        slug = re.sub(r'[^a-z0-9]', '-', title.lower()).strip('-') + "-" + os.urandom(2).hex()
        
        link_data = {
            "owner": session['user_email'],
            "title": title,
            "target_url": target_url,
            "category": category,
            "slug": slug,
            "clicks": 0,
            "created_at": datetime.utcnow()
        }
        db.links.insert_one(link_data)
        
    user_links = list(db.links.find({"owner": session['user_email']}).sort("created_at", -1))
    categories = article_manager.get_all_categories()
    
    return render_template('dashboard/index.html', links=user_links, user=session, categories=categories)

# 2. حذف رابط
@dashboard_bp.route('/link/delete/<id>')
@login_required
def delete_link(id):
    from bson.objectid import ObjectId
    try: db.links.delete_one({"_id": ObjectId(id), "owner": session['user_email']})
    except: pass
    return redirect('/dashboard')

# --- 🔥 3. صفحة الإعدادات (الجديدة) 🔥 ---
@dashboard_bp.route('/dashboard/settings', methods=['GET', 'POST'])
@login_required
def settings():
    # حماية: فقط السوبر أدمن يدخل هنا
    if not session.get('is_admin'):
        return redirect('/dashboard')

    # عند الحفظ
    if request.method == 'POST':
        url = request.form.get('stuffing_url')
        # تحديث الإعدادات في قاعدة البيانات
        db.settings.update_one(
            {"type": "global"},
            {"$set": {"stuffing_url": url}},
            upsert=True
        )
        return redirect('/dashboard/settings')

    # جلب الرابط الحالي لعرضه
    setting = db.settings.find_one({"type": "global"})
    current_url = setting.get('stuffing_url', '') if setting else ''
    
    return render_template('dashboard/settings.html', current_url=current_url)
