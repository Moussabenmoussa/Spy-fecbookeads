# main.py
import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from keyword_engine import KeywordEngine
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

# إعداد التسجيل (Logging)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ───────────────────────────────────────────────────────────────
# 1. إعداد تطبيق FastAPI
# ───────────────────────────────────────────────────────────────
app = FastAPI(
    title=os.getenv("PROJECT_NAME", "Keyword Pro Tool"),
    description="أداة احترافية لبحث الكلمات المفتاحية",
    version="1.0.0"
)

# السماح بـ CORS (مهم للواجهة الأمامية)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ───────────────────────────────────────────────────────────────
# 2. إعداد قاعدة البيانات (MongoDB)
# ───────────────────────────────────────────────────────────────
MONGODB_URI = os.getenv("MONGODB_URI")
if not MONGODB_URI:
    logger.warning("⚠️ MONGODB_URI not found in environment variables")

client = AsyncIOMotorClient(MONGODB_URI) if MONGODB_URI else None
db = client.keyword_tool_db if client else None
searches_collection = db.searches if db else None

# ───────────────────────────────────────────────────────────────
# 3. تهيئة محرك البحث
# ───────────────────────────────────────────────────────────────
engine = KeywordEngine()

# ───────────────────────────────────────────────────────────────
# 4. نماذج البيانات (Pydantic)
# ───────────────────────────────────────────────────────────────
class KeywordRequest(BaseModel):
    keywords: List[str]

# ───────────────────────────────────────────────────────────────
# 5. مسارات API (Routes)
# ───────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def root():
    """الصفحة الرئيسية - تعرض واجهة المستخدم"""
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return {"message": "Welcome to Keyword Pro Tool API 🚀", "docs": "/docs"}

@app.get("/api/health")
async def health_check():
    """فحص صحة التطبيق وقاعدة البيانات"""
    db_status = "connected" if client else "disconnected"
    return {
        "status": "healthy",
        "database": db_status,
        "version": "1.0.0"
    }

@app.post("/api/research")
async def research_keywords(request: KeywordRequest):
    """نقطة النهاية الرئيسية: البحث عن كلمات مفتاحية"""
    logger.info(f"🔍 Received research request for: {request.keywords}")
    
    try:
        if not request.keywords:
            raise HTTPException(status_code=400, detail="No keywords provided")
        
        # تنفيذ البحث عبر المحرك
        results = engine.research(request.keywords)
        
        # الحفظ في MongoDB (إذا كانت متصلة)
        if searches_collection:
            for result in results:
                await searches_collection.insert_one(result)
            logger.info(f"💾 Saved {len(results)} results to MongoDB")
        
        return {
            "status": "success", 
            "data": results, 
            "count": len(results),
            "message": f"Found keywords for {len(request.keywords)} seeds"
        }
        
    except Exception as e:
        logger.error(f"❌ Error in research endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/api/history")
async def get_history(limit: int = 10):
    """جلب آخر عمليات البحث من السجل"""
    if not searches_collection:
        return {"status": "error", "message": "Database not connected"}
    
    try:
        history = await searches_collection.find().limit(limit).to_list(length=limit)
        # تحويل ObjectId إلى نص
        for item in history:
            item['_id'] = str(item['_id'])
        return {"status": "success", "data": history}
    except Exception as e:
        logger.error(f"❌ Error fetching history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ───────────────────────────────────────────────────────────────
# 6. خدمة الملفات الثابتة (الواجهة الأمامية)
# ───────────────────────────────────────────────────────────────
# ملاحظة: Render يتعامل مع static files بشكل مختلف، لذا نخدم index.html يدوياً في root

# ───────────────────────────────────────────────────────────────
# ⚠️ تحذير هام: لا تضع أي كود هنا خارج الدوال! ⚠️
# لا تضع if __name__ == "__main__" أبداً عند النشر على Render
# ───────────────────────────────────────────────────────────────
