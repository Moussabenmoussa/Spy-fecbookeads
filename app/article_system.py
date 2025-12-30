from app import db
from datetime import datetime
import re
import random

class ArticleManager:
    def __init__(self):
        self.articles = db.articles
        self.categories = db.categories  # جدول جديد للأقسام

    # --- 1. معالجة الصور ---
    def optimize_content_images(self, html_content):
        if not html_content: return ""
        pattern = r'src="(https?://[^"]+)"'
        replacement = r'src="https://images.weserv.nl/?url=\1&w=800&output=webp&q=80"'
        return re.sub(pattern, replacement, html_content)

    # --- 2. إدارة المقالات ---
    def add_article(self, title, category, html_body, featured_image):
        clean_body = self.optimize_content_images(html_body)
        article_data = {
            "title": title,
            "category": category.upper().strip(),
            "body": clean_body,
            "image": featured_image,
            "created_at": datetime.utcnow(),
            "views": 0
        }
        return self.articles.insert_one(article_data)

    def get_article_for_visitor(self, category):
        pipeline = [{"$match": {"category": category.upper()}}, {"$sample": {"size": 1}}]
        result = list(self.articles.aggregate(pipeline))
        if result: return result[0]
        fallback = list(self.articles.aggregate([{"$sample": {"size": 1}}]))
        return fallback[0] if fallback else None

    def get_all_articles(self):
        return list(self.articles.find().sort("created_at", -1))

    def delete_article(self, article_id):
        from bson.objectid import ObjectId
        try:
            self.articles.delete_one({"_id": ObjectId(article_id)})
            return True
        except: return False

    # --- 🔥 3. إدارة الأقسام (الجديد) 🔥 ---
    
    def add_category(self, name):
        """إضافة قسم جديد للقاعدة"""
        slug = name.strip().lower().replace(' ', '-')
        # التأكد من عدم التكرار
        if not self.categories.find_one({"slug": slug}):
            self.categories.insert_one({
                "name": name.strip(),
                "slug": slug,
                "created_at": datetime.utcnow()
            })
            return True
        return False

    def get_all_categories(self):
        """جلب كل الأقسام"""
        cats = list(self.categories.find().sort("name", 1))
        # إذا كانت القائمة فارغة (أول مرة)، نضع أقسام افتراضية
        if not cats:
            default_cats = ["General News", "Finance", "Technology", "Health", "Crypto"]
            for c in default_cats: self.add_category(c)
            cats = list(self.categories.find().sort("name", 1))
        return cats

    def delete_category(self, cat_id):
        from bson.objectid import ObjectId
        try:
            self.categories.delete_one({"_id": ObjectId(cat_id)})
            return True
        except: return False
