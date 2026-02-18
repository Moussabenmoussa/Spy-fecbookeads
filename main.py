
# main.py
import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from keyword_engine import KeywordEngine
from dotenv import load_dotenv
from pathlib import Path

# تحميل متغيرات البيئة
load_dotenv()

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Keyword Pro Tool")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB
MONGODB_URI = os.getenv("MONGODB_URI")
client = AsyncIOMotorClient(MONGODB_URI) if MONGODB_URI else None
db = client.keyword_tool_db if client else None
searches_collection = db.searches if db else None

engine = KeywordEngine()

class KeywordRequest(BaseModel):
    keywords: List[str]

# ───────────────────────────────────────────────────────────────
# ✅ الصفحة الرئيسية: تخدم ملف HTML مباشرة
# ───────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    # الحصول على مسار المجلد الحالي بدقة
    base_dir = Path(__file__).resolve().parent
    html_path = base_dir / "static" / "index.html"
    
    logger.info(f"🔍 Looking for frontend at: {html_path}")
    logger.info(f"📁 File exists: {html_path.exists()}")
    
    if html_path.exists():
        logger.info("✅ Serving index.html")
        return FileResponse(html_path)
    else:
        logger.error(f"❌ File not found at: {html_path}")
        # في حال عدم وجود الملف، نعيد رسالة خطأ واضحة في HTML
        return HTMLResponse(
            content="<h1>❌ Frontend Not Found</h1><p>Make sure static/index.html exists in your repo.</p><br><a href='/docs'>Go to API Docs</a>",
            status_code=404
        )

# ───────────────────────────────────────────────────────────────
# مسارات API
# ───────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected" if client else "disconnected",
        "frontend": "loaded" if (Path(__file__).resolve().parent / "static" / "index.html").exists() else "missing"
    }

@app.get("/api/debug")
async def debug_info():
    """معلومات تصحيح الأخطاء"""
    base_dir = Path(__file__).resolve().parent
    return {
        "cwd": os.getcwd(),
        "base_dir": str(base_dir),
        "static_dir": str(base_dir / "static"),
        "index_path": str(base_dir / "static" / "index.html"),
        "index_exists": (base_dir / "static" / "index.html").exists(),
        "static_contents": os.listdir(base_dir / "static") if (base_dir / "static").exists() else "DIR NOT FOUND"
    }

@app.post("/api/research")
async def research_keywords(request: KeywordRequest):
    logger.info(f"🔍 Research request: {request.keywords}")
    try:
        if not request.keywords:
            raise HTTPException(status_code=400, detail="No keywords provided")
        
        results = engine.research(request.keywords)
        
        if searches_collection:
            for result in results:
                await searches_collection.insert_one(result)
        
        return {"status": "success", "data": results, "count": len(results)}
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history")
async def get_history(limit: int = 10):
    if not searches_collection:
        return JSONResponse({"status": "error", "message": "DB not connected"}, status_code=503)
    try:
        history = await searches_collection.find().limit(limit).to_list(length=limit)
        for item in history:
            item['_id'] = str(item['_id'])
        return {"status": "success", "data": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ⚠️ تحذير: لا تضع أي كود تنفيذي هنا (لا if __name__ == "__main__")
