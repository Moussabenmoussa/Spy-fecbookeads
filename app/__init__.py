import os
from flask import Flask
from pymongo import MongoClient

db = None

def create_app():
    global db
    app = Flask(__name__)
    
    # الإعدادات
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'TRAFICOON_KEY_2025')
    
    # قاعدة البيانات
    mongo_uri = os.environ.get('MONGO_URI')
    if mongo_uri:
        try:
            client = MongoClient(mongo_uri.strip())
            db = client['elite_saas_v1']
            print("✅ DB Connected")
        except: print("❌ DB Error")

    # تسجيل الموجهات
    from app.routes.public import public_bp
    app.register_blueprint(public_bp)

    return app
