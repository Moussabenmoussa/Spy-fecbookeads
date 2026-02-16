import os
from pymongo import MongoClient
from datetime import datetime

MONGO_URI = os.getenv("MONGO_URI", "")
client = MongoClient(MONGO_URI)
db = client.get_database("auratools_v2_enterprise")

# المجموعات
tools_col = db["tools"]          # بيانات الأدوات ومحتواها
settings_col = db["settings"]    # إعدادات الموقع (ADSENSE, GSC, META)
usage_col = db["analytics"]      # الإحصائيات

# الإعدادات الافتراضية (Fallback)
DEFAULT_CONFIG = {
    "site_name": "AuraTools Pro",
    "site_description": "Premium Web Utilities",
    "contact_email": "admin@example.com",
    "adsense_code": "",  # كود الإعلان
    "head_code": "",     # كود التحقق والأناليتكس
    "footer_text": "All rights reserved."
}

def get_config():
    """جلب إعدادات الموقع الحالية من القاعدة، أو إنشاء الافتراضية"""
    conf = settings_col.find_one({"_id": "global_config"})
    if not conf:
        settings_col.insert_one({"_id": "global_config", **DEFAULT_CONFIG})
        return DEFAULT_CONFIG
    return conf

def update_config(new_data: dict):
    """تحديث إعدادات الموقع من لوحة التحكم"""
    settings_col.update_one({"_id": "global_config"}, {"$set": new_data}, upsert=True)

def record_usage(tool_slug: str):
    usage_col.update_one(
        {"slug": tool_slug},
        {"$inc": {"count": 1}, "$set": {"last_used": datetime.utcnow()}},
        upsert=True
    )

def get_usage(tool_slug: str):
    doc = usage_col.find_one({"slug": tool_slug})
    return doc["count"] if doc else 0
