# =====================================================================
# ملف: main.py
# المشروع: أداة الاستخلاص النصي من يوتيوب (YouTube Transcript Extractor)
# المعمارية: خادم API + واجهة ويب مدمجة للاختبار (Proof of Concept)
# البيئة: متوافق تماماً مع Render.com و YouTube API v2026
# =====================================================================

import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi

# تهيئة التطبيق
app = FastAPI(title="YouTube Transcript API", version="1.0")

# إعدادات CORS - ضرورية جداً للسماح لتطبيق Flutter بالاتصال بالسيرفر
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# نموذج البيانات المستقبلة
class VideoRequest(BaseModel):
    url: str

# دالة استخراج معرف الفيديو من أي صيغة رابط يوتيوب
def extract_video_id(url: str) -> str:
    # يدعم الروابط: watch?v= , youtu.be/ , shorts/
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None

# =====================================================================
# مسار الواجهة البرمجية (API Endpoint)
# =====================================================================
@app.post("/api/extract")
async def extract_transcript(req: VideoRequest):
    video_id = extract_video_id(req.url)
    
    if not video_id:
        raise HTTPException(status_code=400, detail="رابط يوتيوب غير صالح. تأكد من الرابط.")

    try:
        # المعمارية الحديثة: إنشاء كائن للمكتبة واستخدام دالة list()
        ytt_api = YouTubeTranscriptApi()
        
        # جلب قائمة النصوص المتاحة للفيديو
        transcript_list = ytt_api.list(video_id)
        
        # استخراج أول نص متاح
        transcript_obj = next(iter(transcript_list))
        fetched_transcript = transcript_obj.fetch()
        
        # تجميع النص الكامل في فقرة واحدة متصلة
        full_text = " ".join([entry['text'].replace('\n', ' ') for entry in fetched_transcript])
        full_text = re.sub(r'\s+', ' ', full_text).strip()

        return {
            "success": True,
            "video_id": video_id,
            "language": transcript_obj.language_code,
            "is_generated": transcript_obj.is_generated,
            "full_text": full_text,
            "segments": fetched_transcript
        }

    except Exception as e:
        # معالجة ديناميكية للأخطاء
        error_type = e.__class__.__name__
        if "Disabled" in error_type:
            raise HTTPException(status_code=404, detail="الترجمة معطلة لهذا الفيديو.")
        elif any(x in error_type for x in ["NoTranscript", "Found", "Available"]):
            raise HTTPException(status_code=404, detail="لا توجد ترجمة متاحة لهذا الفيديو.")
        else:
            raise HTTPException(status_code=500, detail=f"خطأ أثناء الاستخراج: {str(e)}")

# =====================================================================
# مسار واجهة الويب للاختبار (Web UI Endpoint)
# =====================================================================
@app.get("/", response_class=HTMLResponse)
async def get_test_ui():
    html_content = """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>يوتيوب إكستراكتور - خادم Render</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;800&display=swap');
            body { font-family: 'Cairo', sans-serif; background-color: #f0f2f5; }
            .loader { border: 3px solid #f3f3f3; border-top: 3px solid #2563eb; border-radius: 50%; width: 20px; height: 20px; animation: spin 1s linear infinite; display: none; }
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        </style>
    </head>
    <body class="min-h-screen flex flex-col items-center py-12">
        <div class="w-full max-w-5xl bg-white p-10 rounded-2xl shadow-2xl border border-gray-100">
            <div class="flex items-center gap-4 mb-8">
                <div class="bg-blue-600 p-3 rounded-lg text-white">
                    <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>
                </div>
                <div>
                    <h1 class="text-3xl font-extrabold text-gray-900">مستخلص نصوص اليوتيوب</h1>
                    <p class="text-gray-500">خادم المعالجة السريع على Render.com</p>
                </div>
            </div>
            
            <div class="flex gap-3 mb-8">
                <input type="text" id="youtubeUrl" placeholder="الصق رابط الفيديو هنا..." class="flex-1 px-5 py-4 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none text-left font-mono" dir="ltr">
                <button onclick="extractText()" class="bg-blue-600 hover:bg-blue-700 text-white font-bold px-8 py-4 rounded-xl flex items-center gap-3 transition-all active:scale-95">
                    <span>استخراج الآن</span>
                    <div id="loadingSpinner" class="loader"></div>
                </button>
            </div>

            <div id="errorBox" class="hidden bg-red-50 border-r-4 border-red-500 text-red-700 p-5 mb-8 rounded-lg animate-pulse"></div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 hidden" id="resultsContainer">
                <div class="flex flex-col">
                    <div class="flex justify-between items-center mb-4">
                        <h2 class="text-lg font-bold text-gray-800">النص الكامل</h2>
                        <button onclick="copyText()" class="text-xs bg-blue-100 text-blue-700 font-bold px-4 py-2 rounded-lg hover:bg-blue-200">نسخ النص</button>
                    </div>
                    <textarea id="fullTextOutput" class="h-[450px] w-full p-5 border border-gray-200 rounded-xl bg-gray-50 text-gray-700 leading-relaxed resize-none focus:outline-none" readonly></textarea>
                </div>

                <div class="flex flex-col">
                    <h2 class="text-lg font-bold text-gray-800 mb-4">البيانات الزمنية (JSON)</h2>
                    <textarea id="jsonOutput" class="h-[450px] w-full p-5 border border-gray-200 rounded-xl bg-gray-900 text-green-400 font-mono text-sm resize-none focus:outline-none" readonly dir="ltr"></textarea>
                </div>
            </div>
        </div>

        <script>
            async function extractText() {
                const url = document.getElementById('youtubeUrl').value;
                const btn = document.querySelector('button span');
                const spinner = document.getElementById('loadingSpinner');
                const errorBox = document.getElementById('errorBox');
                const container = document.getElementById('resultsContainer');
                
                if(!url) return;

                errorBox.classList.add('hidden');
                container.classList.add('hidden');
                btn.textContent = 'جاري المعالجة...';
                spinner.style.display = 'block';

                try {
                    const response = await fetch('/api/extract', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ url: url })
                    });
                    const data = await response.json();
                    if(!response.ok) throw new Error(data.detail || 'خطأ في السيرفر');

                    document.getElementById('fullTextOutput').value = data.full_text;
                    document.getElementById('jsonOutput').value = JSON.stringify(data.segments, null, 2);
                    container.classList.remove('hidden');
                } catch (e) {
                    errorBox.textContent = e.message;
                    errorBox.classList.remove('hidden');
                } finally {
                    btn.textContent = 'استخراج الآن';
                    spinner.style.display = 'none';
                }
            }

            function copyText() {
                const text = document.getElementById('fullTextOutput');
                text.select();
                document.execCommand('copy');
                alert('تم نسخ النص!');
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
