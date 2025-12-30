from flask import Blueprint, render_template, request, redirect, session
from app import db
from datetime import datetime
import re
import os
# استيراد مدير الأقسام
from app.article_system import ArticleManager

dashboard_bp = Blueprint('dashboard', __name__)
article_manager = ArticleManager()

def login_required(f):
    def wrapper(*args, **kwargs):
        if 'user_email' not in session: return redirect('/login')
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

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
            "category": category, # سيتم حفظ اسم القسم
            "slug": slug,
            "clicks": 0,
            "created_at": datetime.utcnow()
        }
        db.links.insert_one(link_data)
        
    user_links = list(db.links.find({"owner": session['user_email']}).sort("created_at", -1))
    
    # 🔥 جلب الأقسام من القاعدة لعرضها في القائمة 🔥
    categories = article_manager.get_all_categories()
    
    return render_template('dashboard/index.html', links=user_links, user=session, categories=categories)

@dashboard_bp.route('/link/delete/<id>')
@login_required
def delete_link(id):
    from bson.objectid import ObjectId
    try: db.links.delete_one({"_id": ObjectId(id), "owner": session['user_email']})
    except: pass
    return redirect('/dashboard')
