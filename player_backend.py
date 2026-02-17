import uvicorn
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

class LoginRequest(BaseModel):
    host: str
    username: str
    password: str

@app.get("/", response_class=HTMLResponse)
async def player_ui(request: Request):
    return templates.TemplateResponse("web_player_ui.html", {"request": request})

# --- وكيل البيانات (API Proxy) ---
@app.post("/api/xtream/{action}")
async def xtream_proxy(action: str, data: LoginRequest, request: Request):
    host = data.host.strip().rstrip("/")
    if not host.startswith("http"):
        host = f"http://{host}"
    
    # 1. تحديد الرابط
    base_url = f"{host}/player_api.php?username={data.username}&password={data.password}"
    target_url = ""

    if action == "auth":
        target_url = base_url
    elif action == "live":
        target_url = f"{base_url}&action=get_live_categories"
    elif action == "vod":
        target_url = f"{base_url}&action=get_vod_categories"
    elif action == "live_streams":
        # هام: نستقبل category_id من الرابط إذا وجد لتقليل الحمل
        cat_id = request.query_params.get("category_id", "")
        target_url = f"{base_url}&action=get_live_streams&category_id={cat_id}"

    if not target_url:
        return {"status": "error", "message": "Invalid Action"}

    # 2. انتحال شخصية مشغل معروف (لتجنب الحظر)
    headers = {
        "User-Agent": "IPTV Smarters Pro/3.1.5 (Linux; Android 10; TV) ExoPlayer/2.9.6",
        "Accept": "*/*"
    }

    # 3. الاتصال
    async with httpx.AsyncClient(verify=False, timeout=60.0) as client:
        try:
            req = client.build_request("GET", target_url, headers=headers)
            r = await client.send(req, stream=True)
            return StreamingResponse(r.aiter_raw(), media_type="application/json")
        except Exception as e:
            return {"status": "error", "message": str(e)}

# --- وكيل البث (Stream Tunnel) ---
# هذا يحل مشكلة تشغيل قنوات HTTP على موقع HTTPS
@app.get("/stream/{host}/{user}/{password}/{stream_id}.{ext}")
async def stream_proxy(host: str, user: str, password: str, stream_id: str, ext: str):
    # إعادة بناء رابط القناة الأصلي
    # فك تشفير الهوست (بسيط) لاستخدامه
    # ملاحظة: نستخدم http افتراضياً لضمان العمل
    stream_url = f"http://{host}/live/{user}/{password}/{stream_id}.{ext}"
    
    async with httpx.AsyncClient(verify=False) as client:
        req = client.build_request("GET", stream_url)
        r = await client.send(req, stream=True)
        return StreamingResponse(r.aiter_raw(), media_type=r.headers.get("content-type"))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
