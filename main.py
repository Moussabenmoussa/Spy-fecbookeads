# =====================================================================
# ملف: main.py
# المشروع: أداة الاستخلاص النصي من يوتيوب (YouTube Transcript Extractor)
# المعمارية: خادم API + واجهة ويب + دعم الكوكيز بتنسيق JSON (تجاوز الحظر)
# التحديث: نظام معالجة JSON Cookies الصارم v3.0
# =====================================================================

import re
import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi

# تهيئة التطبيق
app = FastAPI(title="YouTube Transcript API ULTIMATE", version="3.0")

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

# دالة تحويل ملف JSON الكوكيز إلى قاموس تفهمه المكتبة
def load_json_cookies(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            cookies_data = json.load(f)
            # تحويل قائمة الكوكيز من تنسيق JSON إلى قاموس {name: value}
            return {cookie['name']: cookie['value'] for cookie in cookies_data}
    except Exception:
        return None

# =====================================================================
# مسار الواجهة البرمجية (API Endpoint)
# =====================================================================
@app.post("/api/extract")
async def extract_transcript(req: VideoRequest):
    video_id = extract_video_id(req.url)
    
    if not video_id:
        raise HTTPException(status_code=400, detail="رابط يوتيوب غير صالح.")

    # مسار ملف الكوكيز بتنسيق JSON الذي وفرته أنت
    cookie_path = "cookies.json"
    cookies_dict = None

    if os.path.exists(cookie_path):
        cookies_dict = load_json_cookies(cookie_path)

    try:
        # هندسة الاستخراج باستخدام الكوكيز المحولة من JSON
        if cookies_dict:
            # تمرير القاموس مباشرة للمكتبة
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, cookies=cookie_path)
            # ملاحظة: المكتبة في الإصدارات الحديثة تفضل المسار، 
            # ولكن إذا كان JSON سنستخدم الطريقة التالية لضمان العمل:
            # YouTubeTranscriptApi.get_transcript(video_id, cookies=cookie_path)
        else:
            # محاولة بدون كوكيز
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        
        full_text = " ".join([entry['text'].replace('\n', ' ') for entry in transcript_list])
        full_text = re.sub(r'\s+', ' ', full_text).strip()

        return {
            "success": True,
            "video_id": video_id,
            "full_text": full_text,
            "segments": transcript_list,
            "auth_method": "JSON_Cookies" if cookies_dict else "None"
        }

    except Exception as e:
        error_msg = str(e)
        # تحليل الخطأ لتوجيهك
        if "cookies" in error_msg.lower() or "blocked" in error_msg.lower():
            raise HTTPException(status_code=403, detail="يوتيوب حظر السيرفر. تأكد أن ملف cookies.json حديث.")
        else:
            raise HTTPException(status_code=500, detail=f"خطأ تقني: {error_msg}")

# =====================================================================
# مسار واجهة الويب للاختبار (Web UI Endpoint)
# =====================================================================
@app.get("/", response_class=HTMLResponse)
async def get_test_ui():
    has_json = os.path.exists("cookies.json")
    status_msg = "✅ نظام الكوكيز (JSON) نشط ومحمل" if has_json else "⚠️ السيرفر يعمل بدون كوكيز (خطر الحظر)"
    status_class = "text-green-600 font-bold" if has_json else "text-red-500 font-bold animate-pulse"

    html_content = f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>YouTube Transcript PRO v3</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
            body {{ font-family: 'Cairo', sans-serif; background-color: #f4f7fa; }}
        </style>
    </head>
    <body class="min-h-screen flex flex-col items-center py-12 px-6">
        <div class="w-full max-w-6xl bg-white p-12 rounded-[2.5rem] shadow-2xl border border-gray-100">
            <div class="mb-10 text-center">
                <h1 class="text-4xl font-black text-gray-900 mb-4">مستخلص النصوص <span class="text-blue-600">JSON Edition</span></h1>
                <p class="text-xl {status_class}">{status_msg}</p>
            </div>
            
            <div class="flex flex-col md:flex-row gap-4 mb-12">
                <input type="text" id="youtubeUrl" placeholder="أدخل رابط فيديو يوتيوب هنا..." class="flex-1 px-8 py-5 bg-gray-50 border-2 border-transparent focus:border-blue-500 rounded-2xl outline-none text-left shadow-inner transition-all" dir="ltr">
                <button onclick="extractText()" id="mainBtn" class="bg-blue-600 hover:bg-blue-700 text-white font-black px-12 py-5 rounded-2xl transition-all active:scale-95 shadow-xl">
                    استخراج النص
                </button>
            </div>

            <div id="errorBox" class="hidden bg-red-50 border-r-8 border-red-500 text-red-900 p-8 mb-10 rounded-2xl font-bold shadow-sm"></div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-10 hidden" id="resultsContainer">
                <div class="flex flex-col">
                    <h2 class="text-xl font-bold text-gray-800 mb-4">النص الكامل</h2>
                    <textarea id="fullTextOutput" class="h-[500px] w-full p-8 border border-gray-100 rounded-3xl bg-gray-50 text-gray-800 leading-relaxed resize-none focus:outline-none" readonly></textarea>
                </div>
                <div class="flex flex-col">
                    <h2 class="text-xl font-bold text-gray-800 mb-4">بيانات الـ JSON</h2>
                    <textarea id="jsonOutput" class="h-[500px] w-full p-8 border border-slate-800 rounded-3xl bg-slate-900 text-blue-300 font-mono text-xs resize-none focus:outline-none" readonly dir="ltr"></textarea>
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
                    btn.textContent = 'استخراج النص';
                    btn.disabled = false;
                }}
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
