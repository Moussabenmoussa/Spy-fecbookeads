from flask import Blueprint, render_template, request, redirect, session
from app.article_system import ArticleManager

admin_content_bp = Blueprint('admin_content', __name__)
article_manager = ArticleManager()

# حماية: للأدمن فقط
def admin_required(f):
    def wrapper(*args, **kwargs):
        if not session.get('is_admin'): return redirect('/login')
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

# --- 1. إدارة المقالات ---
@admin_content_bp.route('/admin/articles')
@admin_required
def list_articles():
    articles = article_manager.get_all_articles()
    return render_template('admin/articles_list.html', articles=articles)

@admin_content_bp.route('/admin/articles/new', methods=['GET', 'POST'])
@admin_required
def new_article():
    categories = article_manager.get_all_categories()
    
    if request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category')
        image = request.form.get('image')
        body = request.form.get('body')
        article_manager.add_article(title, category, body, image)
        return redirect('/admin/articles')
        
    return render_template('admin/article_editor.html', categories=categories)

@admin_content_bp.route('/admin/articles/delete/<id>')
@admin_required
def delete_article(id):
    article_manager.delete_article(id)
    return redirect('/admin/articles')

# --- 2. إدارة الأقسام (التصحيح هنا) ---
@admin_content_bp.route('/admin/categories', methods=['GET', 'POST'])
@admin_required
def manage_categories():
    # عند الضغط على زر الإضافة (POST)
    if request.method == 'POST':
        new_cat = request.form.get('category_name')
        if new_cat:
            article_manager.add_category(new_cat)
        # إعادة تحميل الصفحة لتظهر النتيجة
        return redirect('/admin/categories')
    
    # عند العرض العادي (GET)
    categories = article_manager.get_all_categories()
    return render_template('admin/categories_list.html', categories=categories)

@admin_content_bp.route('/admin/categories/delete/<id>')
@admin_required
def delete_category(id):
    article_manager.delete_category(id)
    return redirect('/admin/categories')
