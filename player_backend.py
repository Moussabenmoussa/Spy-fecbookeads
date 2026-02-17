import uvicorn
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# تفعيل CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

# نموذج بيانات الدخول
class LoginRequest(BaseModel):
    host: str
    username: str
    password: str

@app.get("/", response_class=HTMLResponse)
async def player_ui(request: Request):
    return templates.TemplateResponse("web_player_ui.html", {"request": request})

# --- وكيل Xtream السريع (The Tunnel) ---
@app.post("/api/xtream/{action}")
async def xtream_proxy(action: str, data: LoginRequest):
    # تنظيف الرابط
    host = data.host.strip().rstrip("/")
    if not host.startswith("http"):
        host = f"http://{host}"
        
    # بناء رابط الطلب بناءً على نوع العملية
    base_url = f"{host}/player_api.php?username={data.username}&password={data.password}"
    
    target_url = ""
    if action == "auth":
        target_url = base_url # مجرد فحص الدخول
    elif action == "live":
        target_url = f"{base_url}&action=get_live_categories"
    elif action == "vod":
        target_url = f"{base_url}&action=get_vod_categories"
    elif action == "live_streams":
        # جلب القنوات
        target_url = f"{base_url}&action=get_live_streams"
    
    if not target_url:
        return {"status": "error", "message": "Invalid Action"}

    # الاتصال بسيرفر IPTV وتمرير البيانات للمتصفح
    # نستخدم verify=False لأن معظم سيرفرات IPTV لا تملك شهادات SSL صالحة
    async with httpx.AsyncClient(verify=False, timeout=45.0) as client:
        try:
            req = client.build_request("GET", target_url)
            r = await client.send(req, stream=True)
            return StreamingResponse(r.aiter_raw(), media_type="application/json")
        except Exception as e:
            return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
