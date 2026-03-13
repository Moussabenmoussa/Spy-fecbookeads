# =====================================================================
# ملف: main.py
# المشروع: YouTube Professional Transcript Engine (SaaS Edition)
# المعمارية: Playwright Stealth Automation
# الإصدار: v8.1 (التصحيح المعماري للاستيراد)
# =====================================================================

import re
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from playwright.async_api import async_playwright
# تصحيح الاستدعاء المعماري هنا
from playwright_stealth import stealth

app = FastAPI(title="YouTube AI Transcript Pro", version="8.1")

# إعدادات CORS للسماح بالاتصال من أي واجهة (Flutter/Web)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoRequest(BaseModel):
    url: str

def extract_video_id(url: str) -> str:
    # يدعم: watch?v= , youtu.be/ , shorts/
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, url)
    return match.group(1) if match else None

# =====================================================================
# محرك الأتمتة الاحترافي (The Stealth Browser Engine)
# =====================================================================
async def get_transcript_via_browser(video_id: str):
    async with async_playwright() as p:
        # تشغيل المتصفح مع بارامترات لتقليل استهلاك الذاكرة في Render
        browser = await p.chromium.launch(
            headless=True, 
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        # تفعيل بروتوكول التخفي (تم تصحيح الدالة هنا)
        await stealth(page)

        try:
            url = f"https://www.youtube.com/watch?v={video_id}"
            # انتظار تحميل الصفحة (timeout لضمان عدم التعليق)
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)

            # تنفيذ عملية النقر المؤتمتة لاستخراج النص
            # ننتظر ظهور زر الخيارات الإضافية
            await page.wait_for_selector('button[aria-label="More actions"]', timeout=15000)
            await page.click('button[aria-label="More actions"]')
            
            # ننتظر ظهور خيار إظهار النص في القائمة
            await page.wait_for_selector('tp-yt-paper-item:has-text("Show transcript")', timeout=10000)
            await page.click('tp-yt-paper-item:has-text("Show transcript")')
            
            # انتظار ظهور حاوية النص الفعلي
            await page.wait_for_selector('ytd-transcript-segment-renderer', timeout=15000)
            
            # استخراج كافة النصوص والتوقيتات دفعة واحدة عبر JavaScript
            data = await page.evaluate('''() => {
                const results = [];
                const items = document.querySelectorAll('ytd-transcript-segment-renderer');
                items.forEach(item => {
                    const textElement = item.querySelector('.segment-text');
                    const timeElement = item.querySelector('.segment-timestamp');
                    if (textElement && timeElement) {
                        results.push({ text: textElement.innerText, start: timeElement.innerText });
                    }
                });
                return results;
            }''')

            await browser.close()
            
            if not data:
                raise Exception("تعذر العثور على محتوى نصي داخل حاوية النص.")
                
            return data

        except Exception as e:
            await browser.close()
            raise Exception(f"فشل محرك التصفح: {str(e)}")

# =====================================================================
# مسارات الـ API والواجهة
# =====================================================================
@app.post("/api/extract")
async def extract(req: VideoRequest):
    video_id = extract_video_id(req.url)
    if not video_id: 
        raise HTTPException(status_code=400, detail="رابط فيديو غير صالح")

    try:
        segments = await get_transcript_via_browser(video_id)
        full_text = " ".join([s['text'] for s in segments])
        return {
            "success": True, 
            "video_id": video_id, 
            "full_text": full_text, 
            "segments": segments
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=HTMLResponse)
async def ui():
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>YouTube Stealth Engine v8.1</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style> @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap'); body { font-family: 'Cairo', sans-serif; } </style>
    </head>
    <body class="bg-slate-950 text-slate-100 min-h-screen flex flex-col items-center py-16 px-6">
        <div class="w-full max-w-4xl bg-slate-900 p-12 rounded-[2.5rem] border border-slate-800 shadow-2xl">
            <h1 class="text-4xl font-black text-center mb-4">نظام الأتمتة <span class="text-blue-500">v8.1</span></h1>
            <p class="text-center text-slate-400 mb-10">استخراج احترافي عبر محاكاة المتصفح (Playwright)</p>
            
            <div class="flex flex-col gap-4">
                <input id="u" type="text" placeholder="ضع رابط الفيديو هنا..." class="w-full p-6 bg-slate-800 border-2 border-slate-700 rounded-2xl outline-none focus:border-blue-600 text-left text-white" dir="ltr">
                <button onclick="run()" id="b" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-black py-6 rounded-2xl text-xl transition-all shadow-lg shadow-blue-900/40">بدء عملية الاستخراج</button>
            </div>

            <div id="e" class="hidden mt-8 bg-red-900/30 border border-red-500 p-6 rounded-2xl text-red-400 font-bold"></div>
            
            <div id="res" class="hidden mt-10 space-y-4">
                <h2 class="text-xl font-bold">النص المستخرج:</h2>
                <textarea id="t" class="w-full h-[450px] p-8 bg-slate-800 rounded-3xl resize-none outline-none border border-slate-700 leading-relaxed text-slate-300" readonly></textarea>
            </div>
        </div>

        <script>
            async function run() {
                const b = document.getElementById('b'); const u = document.getElementById('u').value;
                const err = document.getElementById('e'); const res = document.getElementById('res');
                if(!u) return;
                
                err.classList.add('hidden'); res.classList.add('hidden');
                b.disabled = true; b.textContent = 'جاري محاكاة المتصفح...';
                
                try {
                    const r = await fetch('/api/extract', {
                        method:'POST', headers:{'Content-Type':'application/json'},
                        body: JSON.stringify({url: u})
                    });
                    const d = await r.json();
                    if(!r.ok) throw new Error(d.detail);
                    document.getElementById('t').value = d.full_text;
                    res.classList.remove('hidden');
                } catch(error) { 
                    err.textContent = error.message; 
                    err.classList.remove('hidden'); 
                } finally { 
                    b.disabled = false; b.textContent = 'بدء عملية الاستخراج'; 
                }
            }
        </script>
    </body>
    </html>
    """)
