from flask import Blueprint, render_template, request, redirect, session, url_for
from app.article_system import ArticleManager

# تعريف الموجه
admin_content_bp = Blueprint('admin_content', __name__)
article_manager = ArticleManager()

# --- حماية: للأدمن فقط ---
def admin_required(f):
    def wrapper(*args, **kwargs):
        if not session.get('user_email') or not session.get('is_admin'):
            return redirect('/login')
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

# 1. صفحة عرض كل المقالات (الجدول)
@admin_content_bp.route('/admin/articles')
@admin_required
def list_articles():
    articles = article_manager.get_all_articles()
    return render_template('admin/articles_list.html', articles=articles)

# 2. صفحة إضافة مقال جديد (المحرر)
@admin_content_bp.route('/admin/articles/new', methods=['GET', 'POST'])
@admin_required
def new_article():
    if request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category')
        image = request.form.get('image')
        body = request.form.get('body')
        
        # استدعاء المحرك للحفظ والمعالجة
        article_manager.add_article(title, category, body, image)
        
        return redirect('/admin/articles')
        
    return render_template('admin/article_editor.html')

# 3. حذف مقال
@admin_content_bp.route('/admin/articles/delete/<id>')
@admin_required
def delete_article(id):
    article_manager.delete_article(id)
    return redirect('/admin/articles')
