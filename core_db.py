import os
from pymongo import MongoClient
from datetime import datetime

# إعدادات الاتصال بالسحابة
MONGO_URI = os.getenv("MONGO_URI", "")
client = MongoClient(MONGO_URI)
db = client.get_database("auratools_production")

# مجموعات البيانات (Collections)
tools_registry = db["tools_registry"] # تخزين محتوى الـ SEO لكل أداة
usage_logs = db["usage_logs"]         # تسجيل إحصائيات الاستخدام للقبول في أدسنس

# إعدادات المنصة (Constants)
PLATFORM_SETTINGS = {
    "brand_name": os.getenv("SITE_NAME", "AuraTools Pro"),
    "base_domain": os.getenv("SITE_DOMAIN", "auratools.onrender.com"),
    "adsense_pub_id": os.getenv("ADSENSE_ID", ""),
    "verify_tag": os.getenv("VERIFY_TAG", ""), # كود التحقق من جوجل
    "admin_user": os.getenv("ADMIN_USER", "admin"),
    "admin_pass": os.getenv("ADMIN_PASS", "Aura2024Pass!")
}

def record_interaction(tool_key: str):
    """
    تسجيل التفاعل البرمجي. 
    جوجل تراقب هذه الإحصائيات لتقييم مدى فائدة الموقع (Utility Score).
    """
    usage_logs.update_one(
        {"tool_id": tool_key},
        {"$inc": {"total_uses": 1}, "$set": {"last_active": datetime.utcnow()}},
        upsert=True
    )

def get_interaction_count(tool_key: str):
    data = usage_logs.find_one({"tool_id": tool_key})
    return data["total_uses"] if data else 0
