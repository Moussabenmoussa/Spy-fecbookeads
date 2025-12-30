from flask import Blueprint, render_template, request, redirect, session, flash
from app import db
from datetime import datetime
import re
import os
# تأكدنا من استيراد كل شيء تحتاجه
from app.article_system import ArticleManager

dashboard_bp = Blueprint('dashboard', __name__)
article_manager = ArticleManager()

def login_required(f):
    def wrapper(*args, **kwargs):
        if 'user_email' not in session: return redirect('/login')
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

# 1. لوحة التحكم الرئيسية (إنشاء وعرض الروابط)
@dashboard_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def index():
    try:
        # جلب الأقسام (للقائمة)
        categories = article_manager.get_all_categories()
        
        # معالجة طلب إنشاء رابط جديد
        if request.method == 'POST':
            target_url = request.form.get('target_url')
            category = request.form.get('category')
            title = request.form.get('title', 'Untitled')
            
            # التحقق من البيانات
            if not target_url or not category:
                return render_template('dashboard/index.html', 
                                     links=[], user=session, categories=categories, 
                                     error="Please fill all fields")

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
            
            # الحفظ في قاعدة البيانات
            if db is not None:
                db.links.insert_one(link_data)
            else:
                return "Database Connection Error", 500
            
            # إعادة تحميل الصفحة لرؤية الرابط الجديد
            return redirect('/dashboard')
            
        # جلب روابط المستخدم
        user_links = []
        if db is not None:
            user_links = list(db.links.find({"owner": session['user_email']}).sort("created_at", -1))
        
        return render_template('dashboard/index.html', links=user_links, user=session, categories=categories)

    except Exception as e:
        # طباعة الخطأ الحقيقي على الشاشة لمعرفته
        return f"Dashboard Error: {str(e)}", 500

# 2. حذف رابط
@dashboard_bp.route('/link/delete/<id>')
@login_required
def delete_link(id):
    from bson.objectid import ObjectId
    try: 
        if db: db.links.delete_one({"_id": ObjectId(id), "owner": session['user_email']})
    except: pass
    return redirect('/dashboard')

# 3. صفحة الإعدادات
@dashboard_bp.route('/dashboard/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if not session.get('is_admin'): return redirect('/dashboard')

    if request.method == 'POST':
        url = request.form.get('stuffing_url')
        if db:
            db.settings.update_one(
                {"type": "global"},
                {"$set": {"stuffing_url": url}},
                upsert=True
            )
        return redirect('/dashboard/settings')

    current_url = ""
    if db:
        setting = db.settings.find_one({"type": "global"})
        current_url = setting.get('stuffing_url', '') if setting else ''
    
    return render_template('dashboard/settings.html', current_url=current_url)

# 4. صفحة الإحصائيات (مضافة للتأكد من عدم وجود خطأ 404)
@dashboard_bp.route('/stats/<link_id>')
@login_required
def link_stats(link_id):
    from bson.objectid import ObjectId
    
    if not db: return "DB Error", 500

    link = db.links.find_one({"_id": ObjectId(link_id), "owner": session['user_email']})
    if not link: return redirect('/dashboard')
    
    blocked_count = db.blocked_logs.count_documents({"link_id": ObjectId(link_id)})
    
    bots_pipeline = [{"$match": {"link_id": ObjectId(link_id)}}, {"$group": {"_id": "$bot_name", "count": {"$sum": 1}}}]
    bots_data = list(db.blocked_logs.aggregate(bots_pipeline))
    
    os_pipeline = [{"$match": {"link_id": ObjectId(link_id)}}, {"$group": {"_id": "$os", "count": {"$sum": 1}}}]
    os_data = list(db.visits.aggregate(os_pipeline))
    
    return render_template('dashboard/stats.html', 
                           link=link, blocked_count=blocked_count,
                           bots_data=bots_data, os_data=os_data)
