# =====================================================================
# ملف: main.py
# المشروع: YouTube Transcript Professional Engine (SaaS Ready)
# المعمارية: Playwright Stealth Automation
# الإصدار: v8.0 (The Professional Choice)
# =====================================================================

import re
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

app = FastAPI(title="YouTube AI Transcript Pro", version="8.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoRequest(BaseModel):
    url: str

def extract_video_id(url: str) -> str:
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, url)
    return match.group(1) if match else None

# =====================================================================
# محرك الأتمتة الاحترافي (Playwright Engine)
# =====================================================================
async def get_transcript_via_browser(video_id: str):
    async with async_playwright() as p:
        # تشغيل المتصفح في وضع الخفاء مع إعدادات تخفي صارمة
        browser = await p.chromium.launch(headless=True)
        # محاكاة سياق متصفح حقيقي (User-Agent, Platform, WebGL)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = await context.new_page()
        # تفعيل بروتوكول التخفي لمنع كشف بيئة السيرفر
        await stealth_async(page)

        try:
            # التوجه لرابط الفيديو
            url = f"https://www.youtube.com/watch?v={video_id}"
            await page.goto(url, wait_until="networkidle")

            # هندسة النقر المؤتمت: فتح قائمة الخيارات ثم "إظهار النص"
            # ملاحظة: يوتيوب يغير واجهته، لذا نستخدم محددات (Selectors) مرنة
            await page.click('button[aria-label="More actions"]')
            await page.wait_for_selector('tp-yt-paper-item:has-text("Show transcript")')
            await page.click('tp-yt-paper-item:has-text("Show transcript")')
            
            # انتظار تحميل حاوية النص
            await page.wait_for_selector('ytd-transcript-segment-renderer')
            
            # استخراج كافة النصوص الزمنية برمجياً
            segments = await page.evaluate('''() => {
                const results = [];
                const lines = document.querySelectorAll('ytd-transcript-segment-renderer');
                lines.forEach(line => {
                    results.append({
                        'text': line.querySelector('.segment-text').innerText,
                        'start': line.querySelector('.segment-timestamp').innerText
                    });
                });
                return results;
            }''')

            await browser.close()
            return segments
        except Exception as e:
            await browser.close()
            raise e

@app.post("/api/extract")
async def extract_transcript(req: VideoRequest):
    video_id = extract_video_id(req.url)
    if not video_id:
        raise HTTPException(status_code=400, detail="رابط يوتيوب غير صالح")

    try:
        # تشغيل المحرك في خيط معالجة منفصل (Async)
        segments = await get_transcript_via_browser(video_id)
        
        full_text = " ".join([s['text'] for s in segments])
        
        return {
            "success": True,
            "video_id": video_id,
            "full_text": full_text,
            "segments": segments
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"فشل المحرك الاحترافي: {str(e)}")

# ملاحظة للمهندس: سيتم إضافة واجهة الويب الاحترافية في الخطوة القادمة
