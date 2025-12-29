from app import db
from datetime import datetime
import bcrypt

class User:
    def __init__(self):
        self.collection = db.users

    def create_user(self, email, password, is_admin=False):
        # تشفير كلمة المرور (Security Standard)
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        user_data = {
            "email": email,
            "password": hashed_pw,
            "plan": "free",  # الخطة الافتراضية
            "is_admin": is_admin,
            "created_at": datetime.utcnow(),
            "cookie_url": "", # رابط الكوكيز الخاص بالمستخدم (فارغ في البداية)
            "subscription_end": None
        }
        
        # التأكد من عدم تكرار الإيميل
        if self.collection.find_one({"email": email}):
            return False
            
        return self.collection.insert_one(user_data)

    def verify_login(self, email, password):
        user = self.collection.find_one({"email": email})
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            return user
        return None

    def get_by_email(self, email):
        return self.collection.find_one({"email": email})
