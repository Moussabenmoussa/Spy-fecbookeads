from flask import Blueprint, render_template, request, redirect, session, make_response
from app import db
from datetime import datetime
import re
import os

dashboard_bp = Blueprint('dashboard', __name__)

# حماية المسارات: لا يدخل إلا من سجل دخوله
def login_required(f):
    def wrapper(*args, **kwargs):
        if 'user_email' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@dashboard_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def index():
    # 1. إنشاء رابط جديد (عند ضغط الزر)
    if request.method == 'POST':
        target_url = request.form.get('target_url')
        category = request.form.get('category', 'general')
        title = request.form.get('title', 'Untitled Link')
        
        # إنشاء Slug عشوائي
        slug = re.sub(r'[^a-z0-9]', '-', title.lower()).strip('-') + "-" + os.urandom(2).hex()
        
        # حفظ في قاعدة البيانات
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
        
    # 2. جلب روابط المستخدم لعرضها في الجدول
    user_links = list(db.links.find({"owner": session['user_email']}).sort("created_at", -1))
    
    return render_template('dashboard/index.html', links=user_links, user=session)

# حذف رابط
@dashboard_bp.route('/link/delete/<id>')
@login_required
def delete_link(id):
    from bson.objectid import ObjectId
    db.links.delete_one({"_id": ObjectId(id), "owner": session['user_email']})
    return redirect('/dashboard')
