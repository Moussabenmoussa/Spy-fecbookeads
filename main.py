# =====================================================================
# ملف: main.py
# المشروع: YouTube Transcript Extractor PRO
# الإصدار: v6.0 (The Bulletproof Edition)
# المعمارية: محول كوكيز + معالج أخطاء ديناميكي + فحص آلي للمكتبة
# =====================================================================

import re
import os
import json
import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import youtube_transcript_api

app = FastAPI(title="YouTube Transcript PRO v6", version="6.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoRequest(BaseModel):
    url: str

def extract_video_id(url: str) -> str:
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, url)
    return match.group(1) if match else None

def convert_json_to_netscape(json_path, output_path):
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            cookies = json.load(f)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Netscape HTTP Cookie File\n")
            for c in cookies:
                domain = c.get('domain', '')
                path = c.get('path', '/')
                secure = "TRUE" if c.get('secure', False) else "FALSE"
                expires = int(c.get('expirationDate', time.time() + 36000))
                name = c.get('name', '')
                value = c.get('value', '')
                f.write(f"{domain}\tTRUE\t{path}\t{secure}\t{expires}\t{name}\t{value}\n")
        return True
    except Exception as e:
        print(f"Conversion Error: {e}")
        return False

# =====================================================================
# محرك الاستخراج الديناميكي
# =====================================================================
@app.post("/api/extract")
async def extract_transcript(req: VideoRequest):
    video_id = extract_video_id(req.url)
    if not video_id:
        raise HTTPException(status_code=400, detail="رابط غير صالح")

    json_cookie_path = "cookies.json"
    netscape_cookie_path = "temp_cookies.txt"
    use_cookies = False

    if os.path.exists(json_cookie_path):
        if convert_json_to_netscape(json_cookie_path, netscape_cookie_path):
            use_cookies = True

    try:
        # هندسة الاستدعاء الديناميكي: البحث عن الكلاس والدالة بأي شكل متاح
        api_class = getattr(youtube_transcript_api, 'YouTubeTranscriptApi', None)
        
        if api_class is None:
            raise Exception("تعذر العثور على كلاس YouTubeTranscriptApi في المكتبة")

        # محاولة الوصول للدالة get_transcript أو list_transcripts
        func = getattr(api_class, 'get_transcript', None)
        
        if func:
            if use_cookies:
                transcript_list = func(video_id, cookies=netscape_cookie_path)
            else:
                transcript_list = func(video_id)
        else:
            raise Exception("المكتبة المثبتة لا تدعم دالة get_transcript. يرجى مراجعة requirements.txt")

        full_text = " ".join([entry['text'].replace('\n', ' ') for entry in transcript_list])
        full_text = re.sub(r'\s+', ' ', full_text).strip()

        return {
            "success": True,
            "video_id": video_id,
            "full_text": full_text,
            "segments": transcript_list
        }

    except Exception as e:
        error_msg = str(e)
        if any(x in error_msg.lower() for x in ["cookies", "ip", "blocked"]):
            raise HTTPException(status_code=403, detail="يوتيوب حظر السيرفر. قم بتحديث cookies.json")
        raise HTTPException(status_code=500, detail=f"خطأ تقني: {error_msg}")

@app.get("/", response_class=HTMLResponse)
async def get_test_ui():
    has_cookies = os.path.exists("cookies.json")
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>YouTube Extractor v6</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style> @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap'); body {{ font-family: 'Cairo', sans-serif; }} </style>
    </head>
    <body class="bg-slate-50 min-h-screen flex flex-col items-center py-12">
        <div class="w-full max-w-5xl bg-white p-12 rounded-[3rem] shadow-xl border border-gray-100">
            <h1 class="text-4xl font-black text-center mb-8">مستخلص النصوص <span class="text-blue-600">v6.0</span></h1>
            <p class="text-center mb-10 {'text-green-600' if has_cookies else 'text-red-600'} font-bold">
                {"✅ ملف cookies.json جاهز" if has_cookies else "⚠️ ملف cookies.json مفقود"}
            </p>
            <div class="flex gap-4 mb-10">
                <input type="text" id="url" placeholder="ضع الرابط هنا..." class="flex-1 p-5 border-2 rounded-2xl outline-none focus:border-blue-500 text-left" dir="ltr">
                <button onclick="run()" id="btn" class="bg-blue-600 text-white font-bold px-12 rounded-2xl">استخراج</button>
            </div>
            <div id="err" class="hidden bg-red-50 p-6 rounded-2xl text-red-800 font-bold mb-6"></div>
            <div id="res" class="hidden grid grid-cols-1 lg:grid-cols-2 gap-8">
                <textarea id="txt" class="h-[500px] p-6 bg-gray-50 rounded-3xl resize-none outline-none border" readonly></textarea>
                <textarea id="json" class="h-[500px] p-6 bg-slate-900 text-green-400 font-mono text-xs rounded-3xl resize-none outline-none" readonly dir="ltr"></textarea>
            </div>
        </div>
        <script>
            async function run() {{
                const url = document.getElementById('url').value;
                const btn = document.getElementById('btn');
                const err = document.getElementById('err');
                const res = document.getElementById('res');
                if(!url) return;
                err.classList.add('hidden');
                btn.disabled = true; btn.textContent = 'جاري العمل...';
                try {{
                    const response = await fetch('/api/extract', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ url: url }})
                    }});
                    const data = await response.json();
                    if(!response.ok) throw new Error(data.detail);
                    document.getElementById('txt').value = data.full_text;
                    document.getElementById('json').value = JSON.stringify(data.segments, null, 2);
                    res.classList.remove('hidden');
                }} catch(e) {{ err.textContent = e.message; err.classList.remove('hidden'); }}
                finally {{ btn.disabled = false; btn.textContent = 'استخراج'; }}
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
