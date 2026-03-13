# =====================================================================
# ملف: main.py
# المشروع: أداة الاستخلاص النصي من يوتيوب (YouTube Transcript Extractor)
# المعمارية: خادم API + واجهة ويب + محول JSON Cookies آلي
# الإصدار: v4.0 (إصدار الاستقرار النهائي)
# =====================================================================

import re
import os
import json
import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
# استدعاء كلاس المكتبة بشكل مباشر وصحيح
from youtube_transcript_api import YouTubeTranscriptApi

# تهيئة التطبيق
app = FastAPI(title="YouTube Transcript API ULTIMATE", version="4.0")

# إعدادات CORS للسماح بالاتصال من تطبيق Flutter مستقبلاً
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# نموذج البيانات المستقبلة من المستخدم
class VideoRequest(BaseModel):
    url: str

# دالة استخراج معرف الفيديو (ID)
def extract_video_id(url: str) -> str:
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, url)
    return match.group(1) if match else None

# دالة هندسية لتحويل JSON إلى تنسيق Netscape الذي تحتاجه المكتبة
def convert_json_to_netscape(json_path, output_path):
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            cookies = json.load(f)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Netscape HTTP Cookie File\n")
            for c in cookies:
                # تحويل القيم المنطقية إلى نص TRUE/FALSE
                domain = c.get('domain', '')
                path = c.get('path', '/')
                secure = "TRUE" if c.get('secure', False) else "FALSE"
                expires = int(c.get('expirationDate', time.time() + 3600))
                name = c.get('name', '')
                value = c.get('value', '')
                
                # صياغة السطر بتنسيق Netscape القياسي
                f.write(f"{domain}\tTRUE\t{path}\t{secure}\t{expires}\t{name}\t{value}\n")
        return True
    except Exception as e:
        print(f"Error converting cookies: {e}")
        return False

# =====================================================================
# مسار الواجهة البرمجية (API Endpoint)
# =====================================================================
@app.post("/api/extract")
async def extract_transcript(req: VideoRequest):
    video_id = extract_video_id(req.url)
    
    if not video_id:
        raise HTTPException(status_code=400, detail="رابط يوتيوب غير صالح.")

    json_cookie_path = "cookies.json"
    netscape_cookie_path = "temp_cookies.txt"

    # التحقق من وجود ملف JSON وتحويله فوراً
    if os.path.exists(json_cookie_path):
        success = convert_json_to_netscape(json_cookie_path, netscape_cookie_path)
        if not success:
            netscape_cookie_path = None
    else:
        netscape_cookie_path = None

    try:
        # استدعاء المكتبة بشكل صحيح (Static Call)
        if netscape_cookie_path:
            # استخدام الملف المحول لتجاوز الحظر
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, cookies=netscape_cookie_path)
        else:
            # محاولة بدون كوكيز (قد تفشل على السيرفر)
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        
        full_text = " ".join([entry['text'].replace('\n', ' ') for entry in transcript_list])
        full_text = re.sub(r'\s+', ' ', full_text).strip()

        return {
            "success": True,
            "video_id": video_id,
            "full_text": full_text,
            "segments": transcript_list,
            "auth": "Netscape_Converted" if netscape_cookie_path else "Direct"
        }

    except Exception as e:
        error_msg = str(e)
        if "cookies" in error_msg.lower() or "IP" in error_msg or "blocked" in error_msg.lower():
            raise HTTPException(status_code=403, detail="يوتيوب حظر السيرفر. حدث ملف cookies.json الخاص بك.")
        else:
            raise HTTPException(status_code=500, detail=f"خطأ تقني: {error_msg}")

# =====================================================================
# مسار واجهة الويب للاختبار (Web UI Endpoint)
# =====================================================================
@app.get("/", response_class=HTMLResponse)
async def get_test_ui():
    has_json = os.path.exists("cookies.json")
    status_msg = "✅ نظام التحويل الذكي (JSON -> Netscape) جاهز" if has_json else "⚠️ السيرفر يفتقد لملف cookies.json"
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>YouTube Transcript PRO v4</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
            body {{ font-family: 'Cairo', sans-serif; background-color: #f8fafc; }}
        </style>
    </head>
    <body class="min-h-screen flex flex-col items-center py-12 px-6">
        <div class="w-full max-w-6xl bg-white p-12 rounded-[3rem] shadow-2xl border border-gray-100">
            <div class="text-center mb-12">
                <h1 class="text-5xl font-black text-slate-900 mb-4 tracking-tight">مستخلص النصوص <span class="text-blue-600 underline">PRO</span></h1>
                <p class="text-lg font-bold {'text-green-600' if has_json else 'text-red-600'}">{status_msg}</p>
            </div>
            
            <div class="flex flex-col md:flex-row gap-5 mb-12">
                <input type="text" id="youtubeUrl" placeholder="أدخل رابط فيديو يوتيوب هنا..." class="flex-1 px-8 py-5 bg-gray-50 border-2 border-gray-100 focus:border-blue-500 rounded-3xl outline-none text-left shadow-inner transition-all text-xl" dir="ltr">
                <button onclick="extractText()" id="mainBtn" class="bg-blue-600 hover:bg-blue-700 text-white font-black px-16 py-5 rounded-3xl transition-all active:scale-95 shadow-2xl shadow-blue-200 text-xl">
                    استخراج
                </button>
            </div>

            <div id="errorBox" class="hidden bg-red-50 border-r-8 border-red-500 text-red-900 p-8 mb-10 rounded-3xl font-bold shadow-md animate-pulse"></div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 hidden" id="resultsContainer">
                <div class="flex flex-col">
                    <h2 class="text-2xl font-black text-gray-800 mb-6">المحتوى النصي الكامل</h2>
                    <textarea id="fullTextOutput" class="h-[600px] w-full p-10 border border-gray-100 rounded-[2.5rem] bg-gray-50 text-gray-800 leading-[2] resize-none focus:outline-none shadow-inner" readonly></textarea>
                </div>
                <div class="flex flex-col">
                    <h2 class="text-2xl font-black text-gray-800 mb-6">هيكل البيانات الزمنية</h2>
                    <textarea id="jsonOutput" class="h-[600px] w-full p-10 border border-slate-800 rounded-[2.5rem] bg-slate-900 text-blue-400 font-mono text-sm resize-none focus:outline-none shadow-2xl" readonly dir="ltr"></textarea>
                </div>
            </div>
        </div>

        <script>
            async function extractText() {{
                const url = document.getElementById('youtubeUrl').value;
                const btn = document.getElementById('mainBtn');
                const errorBox = document.getElementById('errorBox');
                const container = document.getElementById('resultsContainer');
                
                if(!url) return;

                errorBox.classList.add('hidden');
                container.classList.add('hidden');
                btn.textContent = 'جاري المعالجة...';
                btn.disabled = true;

                try {{
                    const response = await fetch('/api/extract', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ url: url }})
                    }});
                    const data = await response.json();
                    if(!response.ok) throw new Error(data.detail || 'خطأ في السيرفر');

                    document.getElementById('fullTextOutput').value = data.full_text;
                    document.getElementById('jsonOutput').value = JSON.stringify(data.segments, null, 2);
                    container.classList.remove('hidden');
                }} catch (e) {{
                    errorBox.textContent = e.message;
                    errorBox.classList.remove('hidden');
                }} finally {{
                    btn.textContent = 'استخراج';
                    btn.disabled = false;
                }}
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
