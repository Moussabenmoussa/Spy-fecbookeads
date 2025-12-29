from flask import Blueprint, render_template, request, redirect, session, url_for
from app.models import User

auth_bp = Blueprint('auth', __name__)
user_model = User()

# صفحة تسجيل الدخول
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = user_model.verify_login(email, password)
        
        if user:
            # إنشاء الجلسة (Session)
            session['user_email'] = user['email']
            session['plan'] = user['plan']
            session['is_admin'] = user.get('is_admin', False)
            
            # توجيه حسب الصلاحية
            if session['is_admin']:
                return redirect('/admin/dashboard')
            else:
                return redirect('/dashboard')
        
        return "Invalid Credentials" # سنحسن التصميم لاحقاً
    
    return render_template('auth/login.html')

# تسجيل خروج
@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')
