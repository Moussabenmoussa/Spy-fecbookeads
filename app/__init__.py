import os
from flask import Flask
from pymongo import MongoClient

# تعريف متغير قاعدة البيانات
db = None

def create_app():
    global db
    app = Flask(__name__)
    
    # 1. إعدادات الأمان
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'TRAFICOON_KEY_2025')
    
    # 2. اتصال قاعدة البيانات
    mongo_uri = os.environ.get('MONGO_URI')
    if mongo_uri:
        try:
            client = MongoClient(mongo_uri.strip())
            db = client['elite_saas_v1']
            print("✅ Database Connected Successfully")
        except Exception as e:
            print(f"❌ Database Connection Error: {e}")

    # 3. تسجيل الموجهات (تمت إضافة لوحة التحكم هنا)
    from app.routes.public import public_bp
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp  # <--- هذا هو السطر الجديد
    
    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)       # <--- وهذا أيضاً لتفعيل اللوحة

    return app
