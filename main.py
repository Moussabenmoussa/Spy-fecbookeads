import os
import uvicorn
import json
from datetime import datetime
from typing import Dict, Any
from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, Response, StreamingResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from pymongo import MongoClient
import seo_utils  # ملف الأدوات الذي أنشأناه سابقاً

# --- CONFIG ---
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Render Env Vars
MONGO_URI = os.environ.get("MONGO_URI")
ADMIN_PASSWORD = os.environ.get("SECRET_KEY", "admin123")

# DB Connection
try:
    client = MongoClient(MONGO_URI)
    db = client["pseo_engine"]
    projects_col = db["projects"]
    pages_col = db["pages"]
    print("✅ MongoDB Connected")
except Exception as e:
    print(f"❌ DB Error: {e}")

# --- MODELS ---
class ManualPageRequest(BaseModel):
    password: str
    project_slug: str
    slug: str
    title: str
    html_content: str  # المحتوى الذي ستلصقه من Gemini
    variables: Dict[str, Any]

class PromptRequest(BaseModel):
    device: str
    country: str
    app_name: str

# --- ROUTES: ADMIN API ---

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

@app.post("/api/generate-master-prompt")
async def generate_prompt(req: PromptRequest):
    """
    يولد البرومبت القائد لتأخذه إلى Gemini
    """
    master_prompt = f"""
    تصرف كخبير سيو تقني ومحترف في أنظمة البث.
    المهمة: اكتب مقالاً تفصيلياً وحصرياً بتنسيق HTML (فقط Body tags) حول الموضوع التالي:
    "كيفية إعداد وتشغيل اشتراك IPTV على جهاز {req.device} للمستخدمين في {req.country}".
    
    الشروط التقنية:
    1. استخدم وسوم <h2> و <h3> و <ul> و <p> لتنسيق المقال.
    2. لا تضع وسم <html> أو <head> أو <body>، ابدأ بالمحتوى مباشرة.
    3. ركز على تطبيق {req.app_name} كأفضل خيار لهذا الجهاز.
    4. أضف فقرة تحذيرية خاصة بقوانين الإنترنت في {req.country}.
    5. اجعل النبرة خبيرة، حيادية، ومقنعة.
    6. أضف جدولاً للمواصفات التقنية (Table) يقارن بين التطبيقات.
    7. الكلمات المفتاحية التي يجب دمجها بذكاء: 4K streaming, Anti-freeze, Setup Guide.
    
    الهدف: إقناع القارئ بأن هذا هو الحل الوحيد المستقر.
    """
    return {"prompt": master_prompt}

@app.post("/api/publish-manual")
async def publish_manual_page(req: ManualPageRequest):
    if req.password != ADMIN_PASSWORD:
        raise HTTPException(403, "Invalid Password")
    
    # التحقق من عدم التكرار
    if pages_col.find_one({"slug": req.slug, "project_slug": req.project_slug}):
        return {"status": "error", "message": "هذه الصفحة موجودة بالفعل!"}

    # حفظ الصفحة في قاعدة البيانات
    page_doc = {
        "project_slug": req.project_slug,
        "slug": req.slug,
        "title": req.title,
        "variables": req.variables,
        "content": req.html_content,  # المحتوى اليدوي عالي الجودة
        "type": "manual",  # لتمييزها عن الآلي
        "status": "published",
        "created_at": datetime.now()
    }
    
    pages_col.insert_one(page_doc)
    return {"status": "success", "message": "تم نشر المقال بنجاح ✅", "url": f"/p/{req.project_slug}/{req.slug}"}

# --- ROUTES: PUBLIC VIEW ---

@app.get("/p/{project_slug}/{page_slug}", response_class=HTMLResponse)
async def view_page(request: Request, project_slug: str, page_slug: str):
    page = pages_col.find_one({"slug": page_slug, "project_slug": project_slug})
    if not page:
        raise HTTPException(404, "Article not found")
        
    # جلب إعدادات المشروع (للرابط والدومين)
    project = projects_col.find_one({"slug": project_slug})
    
    # نستخدم قالباً عاماً ونحقن فيه المحتوى اليدوي
    return templates.TemplateResponse("generated_page.html", {
        "request": request,
        "page": page,
        "project": project,
        "content_html": page["content"] # المحتوى الجاهز من Gemini
    })

# Sitemap & Other routes remain similar...

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
