import os, json, re
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# --- تنظيف الرابط بشكل عدواني من أي رموز مخفية للهواتف ---
raw_uri = os.getenv("MONGO_URI", "")
# حذف أي مسافات، أسطر جديدة، أو رموز غريبة في بداية ونهاية الرابط
MONGO_URI = re.sub(r'[\s\n\r]', '', raw_uri).strip()

try:
    if not MONGO_URI:
        print("⚠️ تحذير: لم يتم العثور على رابط MONGO_URI")
        ads_collection = None
    else:
        # طباعة طول الرابط للتأكد (اختياري للديبيغ)
        print(f"🔗 محاولة الاتصال برابط طوله: {len(MONGO_URI)}")
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client.get_database() # سيأخذ الاسم من الرابط تلقائياً
        ads_collection = db['ads']
        # اختبار الاتصال
        client.admin.command('ping')
        print("✅ اتصلت بقاعدة البيانات بنجاح!")
except Exception as e:
    print(f"❌ خطأ الاتصال: {e}")
    ads_collection = None
