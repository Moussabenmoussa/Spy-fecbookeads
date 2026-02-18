from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from keyword_engine import KeywordEngine

load_dotenv()

app = FastAPI(title=os.getenv("PROJECT_NAME", "Keyword Pro Tool"))

# السماح بالوصول من جميع المصادر (للتطوير)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# الاتصال بقاعدة البيانات
client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
db = client.keyword_tool_db
searches_collection = db.searches

# محرك البحث
engine = KeywordEngine()

class KeywordRequest(BaseModel):
    keywords: List[str]

@app.post("/api/research")
async def research_keywords(request: KeywordRequest):
    try:
        if not request.keywords:
            raise HTTPException(status_code=400, detail="No keywords provided")
        
        # تنفيذ البحث
        results = engine.research(request.keywords)
        
        # حفظ في قاعدة البيانات
        for result in results:
            await searches_collection.insert_one(result)
        
        return {"status": "success", "data": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history")
async def get_history(limit: int = 10):
    history = await searches_collection.find().limit(limit).to_list(length=limit)
    for item in history:
        item['_id'] = str(item['_id'])
    return {"status": "success", "data": history}

@app.get("/")
async def root():
    return {"message": "Welcome to Keyword Pro Tool API"}

# تشغيل الخادم
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
