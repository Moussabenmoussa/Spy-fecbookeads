from app import db
from datetime import datetime
import re
import random

class ArticleManager:
    def __init__(self):
        # الاتصال بجداول المقالات والأقسام
        self.articles = db.articles
        self.categories = db.categories

    # --- 1. خوارزمية تحسين الصور (Auto-WebP) ---
    def optimize_content_images(self, html_content):
        """
        تحويل أي صورة داخل المقال إلى صيغة WebP السريعة
        باستخدام خدمة سحابية مجانية (weserv.nl)
        """
        if not html_content: return ""
        
        # البحث عن روابط الصور واستبدالها
        pattern = r'src="(https?://[^"]+)"'
        replacement = r'src="https://images.weserv.nl/?url=\1&w=800&output=webp&q=80"'
        
        return re.sub(pattern, replacement, html_content)

    # --- 2. إضافة مقال + إنشاء القسم تلقائياً ---
    def add_article(self, title, category, html_body, featured_image):
        # أ. معالجة الصور داخل النص
        clean_body = self.optimize_content_images(html_body)
        
        # ب. تنظيف اسم القسم
        cat_name_clean = category.strip() # الاسم كما كتبه الأدمن (مثلاً: Crypto Currency)
        cat_code = cat_name_clean.upper() # الاسم البرمجي (CRYPTO CURRENCY)
        
        # ج. تجهيز بيانات المقال
        article_data = {
            "title": title,
            "category": cat_code,
            "body": clean_body,
            "image": featured_image,
            "created_at": datetime.utcnow(),
            "views": 0
        }
        
        # د. 🔥 السحر هنا: إنشاء القسم أوتوماتيكياً إذا لم يكن موجوداً 🔥
        slug = cat_name_clean.lower().replace(' ', '-')
        
        # نبحث هل هذا القسم موجود؟
        if not self.categories.find_one({"slug": slug}):
            # إذا غير موجود، ننشئه فوراً
            self.categories.insert_one({
                "name": cat_name_clean.title(), # Crypto Currency
                "slug": slug,                   # crypto-currency
                "created_at": datetime.utcnow()
            })

        # هـ. حفظ المقال
        return self.articles.insert_one(article_data)

    # --- 3. جلب مقال للزائر (حسب القسم) ---
    def get_article_for_visitor(self, category):
        """يختار مقالاً عشوائياً من نفس القسم ليعرضه للزائر"""
        pipeline = [
            {"$match": {"category": category.upper()}},
            {"$sample": {"size": 1}}
        ]
        result = list(self.articles.aggregate(pipeline))
        
        if result:
            return result[0]
            
        # خطة بديلة: إذا القسم فارغ، هات أي مقال عام
        fallback = list(self.articles.aggregate([{"$sample": {"size": 1}}]))
        return fallback[0] if fallback else None

    # --- 4. أدوات الأدمن ---
    
    # جلب قائمة المقالات
    def get_all_articles(self):
        return list(self.articles.find().sort("created_at", -1))

    # حذف مقال
    def delete_article(self, article_id):
        from bson.objectid import ObjectId
        try:
            self.articles.delete_one({"_id": ObjectId(article_id)})
            return True
        except:
            return False
            
    # جلب قائمة الأقسام (لعرضها في لوحة المستخدم لإنشاء الروابط)
    def get_all_categories(self):
        return list(self.categories.find().sort("name", 1))
