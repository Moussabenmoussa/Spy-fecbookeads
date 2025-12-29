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





# --- 👇 أضف هذا الكود في نهاية الملف لإنشاء حسابك 👇 ---

@auth_bp.route('/setup-master-admin')
def setup_master():
    # 1. تفاصيل حسابك (يمكنك تغييرها هنا)
    admin_email = "admin@traficoon.com"
    admin_pass = "123456" # غيرها لاحقاً
    
    # 2. إنشاء الحساب في قاعدة البيانات
    try:
        user_model.create_user(email=admin_email, password=admin_pass, is_admin=True)
        return f"""
        <h1 style='color:green; text-align:center; margin-top:50px;'>
            ✅ Admin Created Successfully!<br>
            <span style='color:black; font-size:16px;'>Email: {admin_email}<br>Pass: {admin_pass}</span><br>
            <a href='/login'>Go to Login</a>
        </h1>
        """
    except Exception as e:
        return f"Error: {e}"
