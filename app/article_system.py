from app import db
from datetime import datetime
import re
import random

class ArticleManager:
    def __init__(self):
        # الاتصال بجدول المقالات
        self.collection = db.articles

    # --- 1. الخوارزمية الذكية لتحسين الصور (Auto-WebP) ---
    def optimize_content_images(self, html_content):
        """
        هذه الدالة تبحث عن أي صورة داخل كود HTML
        وتقوم بتغليفها بخدمة CDN لتحويلها إلى WebP وسريع التحميل.
        """
        if not html_content: return ""
        
        # البحث عن روابط الصور src="..."
        # واستبدالها برابط المعالجة السحابية
        pattern = r'src="(https?://[^"]+)"'
        # نستخدم خدمة images.weserv.nl المجانية والموثوقة عالمياً للتحويل
        replacement = r'src="https://images.weserv.nl/?url=\1&w=800&output=webp&q=80"'
        
        optimized_html = re.sub(pattern, replacement, html_content)
        return optimized_html

    # --- 2. إضافة مقال جديد ---
    def add_article(self, title, category, html_body, featured_image):
        # أ. تحسين الصور داخل النص تلقائياً
        clean_body = self.optimize_content_images(html_body)
        
        # ب. تجهيز البيانات
        article_data = {
            "title": title,
            "category": category.upper().strip(), # توحيد الأقسام بحروف كبيرة
            "body": clean_body,
            "image": featured_image, # الصورة البارزة
            "created_at": datetime.utcnow(),
            "views": 0
        }
        
        # ج. الحفظ في القاعدة
        return self.collection.insert_one(article_data)

    # --- 3. جلب مقال ذكي (حسب القسم) ---
    def get_article_for_visitor(self, category):
        """
        تختار مقالاً عشوائياً من نفس القسم الذي طلبه الزائر.
        إذا لم تجد، تأتي بمقال عام (General).
        """
        # محاولة العثور على مقال في نفس القسم
        pipeline = [
            {"$match": {"category": category.upper()}},
            {"$sample": {"size": 1}} # اختيار عشوائي لتبدو المجلة متجددة
        ]
        result = list(self.collection.aggregate(pipeline))
        
        if result:
            return result[0]
            
        # خطة بديلة: إذا لم نجد مقالاً في هذا القسم، هات أي مقال
        fallback = list(self.collection.aggregate([{"$sample": {"size": 1}}]))
        return fallback[0] if fallback else None

    # --- 4. جلب كل المقالات (للأدمن) ---
    def get_all_articles(self):
        return list(self.collection.find().sort("created_at", -1))

    # --- 5. حذف مقال ---
    def delete_article(self, article_id):
        from bson.objectid import ObjectId
        try:
            self.collection.delete_one({"_id": ObjectId(article_id)})
            return True
        except:
            return False
