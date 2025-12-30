from flask import Blueprint, render_template, request, redirect, session
from app import db
from datetime import datetime
import re
import os
from app.article_system import ArticleManager
from bson.objectid import ObjectId # استيراد مهم

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
    try:
        categories = []
        if db: categories = article_manager.get_all_categories()
        if not categories:
            categories = [{'name': 'General News', 'slug': 'general'}, {'name': 'Finance', 'slug': 'finance'}]

        if request.method == 'POST':
            target_url = request.form.get('target_url')
            category = request.form.get('category')
            title = request.form.get('title', 'Untitled')
            
            if not target_url: return redirect('/dashboard')

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
            if db: db.links.insert_one(link_data)
            return redirect('/dashboard')
            
        user_links = []
        if db: user_links = list(db.links.find({"owner": session['user_email']}).sort("created_at", -1))
        
        return render_template('dashboard/index.html', links=user_links, user=session, categories=categories)
    except Exception as e:
        return f"Dashboard Index Error: {e}", 500

# 2. حذف رابط
@dashboard_bp.route('/link/delete/<id>')
@login_required
def delete_link(id):
    try: 
        if db: db.links.delete_one({"_id": ObjectId(id), "owner": session['user_email']})
    except: pass
    return redirect('/dashboard')

# 3. الإعدادات
@dashboard_bp.route('/dashboard/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if not session.get('is_admin'): return redirect('/dashboard')
    if request.method == 'POST':
        url = request.form.get('stuffing_url')
        if db: db.settings.update_one({"type": "global"}, {"$set": {"stuffing_url": url}}, upsert=True)
        return redirect('/dashboard/settings')
    current_url = ""
    if db:
        setting = db.settings.find_one({"type": "global"})
        current_url = setting.get('stuffing_url', '') if setting else ''
    return render_template('dashboard/settings.html', current_url=current_url)

# 4. 🔥 صفحة الإحصائيات (مصححة ومحمية) 🔥
@dashboard_bp.route('/stats/<link_id>')
@login_required
def link_stats(link_id):
    try:
        if not db: return "Database Disconnected", 500

        # التحقق من صحة المعرف
        try:
            oid = ObjectId(link_id)
        except:
            return "Invalid Link ID", 400

        # جلب الرابط
        link = db.links.find_one({"_id": oid, "owner": session['user_email']})
        if not link: return redirect('/dashboard')
        
        # جلب الإحصائيات (مع معالجة القوائم الفارغة)
        blocked_count = db.blocked_logs.count_documents({"link_id": oid})
        
        bots_data = list(db.blocked_logs.aggregate([
            {"$match": {"link_id": oid}},
            {"$group": {"_id": "$bot_name", "count": {"$sum": 1}}}
        ]))
        
        os_data = list(db.visits.aggregate([
            {"$match": {"link_id": oid}},
            {"$group": {"_id": "$os", "count": {"$sum": 1}}}
        ]))
        
        return render_template('dashboard/stats.html', 
                               link=link, 
                               blocked_count=blocked_count,
                               bots_data=bots_data, 
                               os_data=os_data)
    except Exception as e:
        # هذا سيطبع سبب الخطأ بدقة
        return f"Stats Error: {str(e)}", 500
