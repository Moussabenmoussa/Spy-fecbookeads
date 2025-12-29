from flask import Blueprint, render_template, request, redirect, session, url_for
from app.models import User

auth_bp = Blueprint('auth', __name__)
user_model = User()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = user_model.verify_login(email, password)
        
        if user:
            # تسجيل بيانات الجلسة
            session['user_email'] = user['email']
            session['plan'] = user.get('plan', 'free')
            session['is_admin'] = user.get('is_admin', False)
            
            # 🔥 التصحيح: توجيه الجميع للوحة التحكم الموحدة
            return redirect('/dashboard')
        
        return render_template('auth/login.html', error="Invalid email or password")
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# رابط الطوارئ لإنشاء الأدمن (يمكنك حذفه لاحقاً)
@auth_bp.route('/setup-master-admin')
def setup_master():
    admin_email = "admin@traficoon.com"
    admin_pass = "123456"
    try:
        user_model.create_user(email=admin_email, password=admin_pass, is_admin=True)
        return "Admin Created. Go to /login"
    except:
        return "Admin already exists or error."
