import uvicorn
import httpx
from fastapi import FastAPI, Request, Response
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

# Headers للتنكر وكأننا تطبيق مشغل فيديو حقيقي
FAKE_HEADERS = {
    "User-Agent": "VLC/3.0.18 LibVLC/3.0.18",
    "Accept": "*/*"
}

@app.get("/", response_class=HTMLResponse)
async def player_ui(request: Request):
    return templates.TemplateResponse("web_player_ui.html", {"request": request})

# --- وكيل البيانات (مع التنكر) ---
@app.post("/api/xtream/{action}")
async def xtream_proxy(action: str, data: LoginRequest, request: Request):
    host = data.host.strip().rstrip("/")
    if not host.startswith("http"): host = f"http://{host}"
    
    base_url = f"{host}/player_api.php?username={data.username}&password={data.password}"
    
    target_url = ""
    if action == "auth": target_url = base_url
    elif action == "live": target_url = f"{base_url}&action=get_live_categories"
    elif action == "vod": target_url = f"{base_url}&action=get_vod_categories"
    elif action == "live_streams":
        cat_id = request.query_params.get("category_id", "")
        target_url = f"{base_url}&action=get_live_streams&category_id={cat_id}"
    
    if not target_url: return {"status": "error"}

    async with httpx.AsyncClient(verify=False, timeout=60.0) as client:
        try:
            # نرسل الهيدرز المزيفة ليقبل السيرفر الطلب
            req = client.build_request("GET", target_url, headers=FAKE_HEADERS)
            r = await client.send(req)
            return Response(content=r.content, media_type="application/json")
        except Exception as e:
            return {"status": "error", "message": str(e)}

# --- وكيل البث (The Stream Tunnel) ---
# هذا هو الحل للشاشة السوداء: الفيديو يمر عبر سيرفرنا
@app.get("/stream_proxy")
async def stream_tunnel(url: str):
    async with httpx.AsyncClient(verify=False, timeout=30.0) as client:
        try:
            req = client.build_request("GET", url, headers=FAKE_HEADERS)
            r = await client.send(req, stream=True)
            return StreamingResponse(r.aiter_raw(), media_type=r.headers.get("content-type"))
        except:
            return Response(status_code=404)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
