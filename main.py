# main.py - نظيف 100% لـ Render
import os
import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List
from motor.motor_asyncio import AsyncIOMotorClient
from keyword_engine import KeywordEngine
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ───────────────────────────────────────────────────────────────
# 1. تطبيق FastAPI
# ───────────────────────────────────────────────────────────────
app = FastAPI(title="Keyword Pro Tool")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ───────────────────────────────────────────────────────────────
# 2. قاعدة البيانات
# ───────────────────────────────────────────────────────────────
MONGODB_URI = os.getenv("MONGODB_URI")
client = AsyncIOMotorClient(MONGODB_URI) if MONGODB_URI else None
db = client.keyword_tool_db if client else None
searches_collection = db.searches if db else None

engine = KeywordEngine()

# ───────────────────────────────────────────────────────────────
# 3. النماذج
# ───────────────────────────────────────────────────────────────
class KeywordRequest(BaseModel):
    keywords: List[str]

# ───────────────────────────────────────────────────────────────
# 4. المسارات (Routes) - فقط دوال، لا يوجد كود خارجي
# ───────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    """خدمة واجهة المستخدم"""
    base_dir = Path(__file__).resolve().parent
    html_path = base_dir / "static" / "index.html"
    
    if html_path.exists():
        return FileResponse(html_path)
    return JSONResponse(
        status_code=404,
        content={"error": "Frontend not found", "docs": "/docs"}
    )

@app.get("/api/health")
async def health():
    """فحص الصحة"""
    base_dir = Path(__file__).resolve().parent
    return {
        "status": "healthy",
        "database": "connected" if client else "disconnected",
        "frontend_exists": (base_dir / "static" / "index.html").exists()
    }

@app.get("/api/debug")
async def debug():
    """معلومات التصحيح"""
    base_dir = Path(__file__).resolve().parent
    static_dir = base_dir / "static"
    return {
        "cwd": os.getcwd(),
        "base_dir": str(base_dir),
        "static_exists": static_dir.exists(),
        "index_exists": (static_dir / "index.html").exists(),
        "static_files": os.listdir(static_dir) if static_dir.exists() else []
    }

@app.post("/api/research")
async def research(request: KeywordRequest):
    """نقطة البحث الرئيسية"""
    logger.info(f"🔍 Request: {request.keywords}")
    try:
        if not request.keywords:
            raise HTTPException(400, "No keywords provided")
        
        results = engine.research(request.keywords)
        
        if searches_collection:
            for r in results:
                await searches_collection.insert_one(r)
        
        return {"status": "success", "data": results, "count": len(results)}
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise HTTPException(500, str(e))

@app.get("/api/history")
async def history(limit: int = 10):
    """سجل البحث"""
    if not searches_collection:
        return JSONResponse({"error": "DB not connected"}, status_code=503)
    try:
        items = await searches_collection.find().limit(limit).to_list(limit)
        for item in items:
            item['_id'] = str(item['_id'])
        return {"status": "success", "data": items}
    except Exception as e:
        raise HTTPException(500, str(e))

# ───────────────────────────────────────────────────────────────
# ⚠️ STOP: لا تضع أي كود بعد هذا السطر! ⚠️
# لا if __name__ == "__main__"
# لا print() خارج الدوال
# لا تنفيذ أي دالة هنا
# ───────────────────────────────────────────────────────────────
