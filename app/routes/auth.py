from flask import Blueprint, render_template, request, redirect, session
from app.models import User

auth_bp = Blueprint('auth', __name__)
user_model = User()

# --- تسجيل الدخول ---
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
            return redirect('/dashboard')
        
        return render_template('auth/login.html', error="Invalid email or password")
    
    return render_template('auth/login.html')

# --- 🔥 تسجيل حساب جديد (الجديد) 🔥 ---
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # 1. التحقق من صحة البيانات (بسيط)
        if not email or not password:
            return render_template('auth/register.html', error="Please fill all fields")

        # 2. محاولة إنشاء المستخدم
        # ملاحظة: create_user في models.py تقوم تلقائياً بجعله 'free' و 'is_admin=False'
        result = user_model.create_user(email, password)
        
        if result:
            # نجاح التسجيل -> توجيه لصفحة الدخول
            return redirect('/login')
        else:
            # فشل (غالباً الإيميل مكرر)
            return render_template('auth/register.html', error="Email already exists!")

    return render_template('auth/register.html')

# --- تسجيل الخروج ---
@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# رابط الطوارئ للأدمن (احتفظ به للطوارئ أو احذفه إذا انتهيت)
@auth_bp.route('/setup-master-admin')
def setup_master():
    try:
        user_model.create_user(email="admin@traficoon.com", password="123456", is_admin=True)
        return "Admin Created."
    except: return "Error."
