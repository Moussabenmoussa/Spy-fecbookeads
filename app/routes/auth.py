from flask import Blueprint, render_template, request, redirect, session
from app.models import User

auth_bp = Blueprint('auth', __name__)
user_model = User()

# --- 1. تسجيل الدخول ---
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = user_model.verify_login(email, password)
        
        if user:
            session['user_email'] = user['email']
            session['plan'] = user.get('plan', 'free')
            session['is_admin'] = user.get('is_admin', False)
            # إذا كان أدمن يذهب للوحة، وإلا للمستخدم
            return redirect('/dashboard')
        
        return render_template('auth/login.html', error="Invalid email or password")
    
    return render_template('auth/login.html')

# --- 2. 🔥 تسجيل حساب جديد (هذا هو الكود الناقص) 🔥 ---
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # عند الضغط على زر "Create Account"
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            return render_template('auth/register.html', error="All fields required")

        # محاولة إنشاء المستخدم
        if user_model.create_user(email, password):
            # نجح -> اذهب للدخول
            return redirect('/login')
        else:
            # فشل -> الإيميل موجود مسبقاً
            return render_template('auth/register.html', error="Email already exists!")

    # عند فتح الصفحة
    return render_template('auth/register.html')

# --- 3. الخروج ---
@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')
