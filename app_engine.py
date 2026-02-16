import os
from fastapi import FastAPI, Request, Form, File, UploadFile, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from datetime import datetime

from core_db import tools_col, get_config, update_config, get_usage, settings_col
from tool_logic import ToolEngine

app = FastAPI()
templates = Jinja2Templates(directory="templates")
security = HTTPBasic()

# --- حقن الإعدادات في كل القوالب ---
@app.middleware("http")
async def add_global_config(request: Request, call_next):
    request.state.config = get_config()
    response = await call_next(request)
    return response

# --- التأسيس التلقائي (الذكي) ---
@app.on_event("startup")
def seed_db():
    # التأكد من وجود الأدوات الأساسية
    if tools_col.count_documents({}) == 0:
        tools = [
            {
                "slug": "webp-pro",
                "title": "WebP Converter Ultimate",
                "short_desc": "Convert images to WebP format instantly.",
                "seo_content": "<h2>Why WebP?</h2><p>WebP is a modern image format...</p>", # محتوى افتراضي
                "guide": "Upload image -> Click Convert -> Download."
            },
            {
                "slug": "qr-generator",
                "title": "QR Code Generator",
                "short_desc": "Create secure QR codes for free.",
                "seo_content": "<h2>QR Technology</h2><p>Quick Response codes are...</p>",
                "guide": "Enter text -> Click Generate."
            }
        ]
        tools_col.insert_many(tools)

# --- الحماية ---
def admin_auth(creds: HTTPBasicCredentials = Depends(security)):
    user = os.getenv("ADMIN_USER", "admin")
    pw = os.getenv("ADMIN_PASS", "admin123")
    if creds.username != user or creds.password != pw:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return creds.username

# --- الواجهة العامة ---

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    tools = list(tools_col.find())
    return templates.TemplateResponse("layout_tool.html", {
        "request": request, "tools": tools, "active": None, "config": request.state.config
    })

@app.get("/tool/{slug}", response_class=HTMLResponse)
async def tool_view(request: Request, slug: str):
    tool = tools_col.find_one({"slug": slug})
    if not tool: raise HTTPException(404)
    usage = get_usage(slug)
    return templates.TemplateResponse("layout_tool.html", {
        "request": request, "active": tool, "config": request.state.config, "usage": usage
    })

# الصفحات القانونية الديناميكية
@app.get("/privacy-policy", response_class=HTMLResponse)
async def privacy(request: Request):
    cfg = request.state.config
    content = f"""
    <div class="prose max-w-none">
        <h1>Privacy Policy for {cfg['site_name']}</h1>
        <p>At {cfg['site_name']}, accessible from the web, one of our main priorities is the privacy of our visitors.</p>
        <p>If you have additional questions or require more information about our Privacy Policy, do not hesitate to contact us at {cfg['contact_email']}.</p>
        <h2>Log Files</h2>
        <p>{cfg['site_name']} follows a standard procedure of using log files...</p>
    </div>
    """
    return templates.TemplateResponse("layout_tool.html", {
        "request": request, "static_content": content, "config": cfg
    })

@app.get("/terms", response_class=HTMLResponse)
async def terms(request: Request):
    cfg = request.state.config
    content = f"""
    <div class="prose max-w-none">
        <h1>Terms of Service</h1>
        <p>By using {cfg['site_name']}, you agree to these terms.</p>
    </div>
    """
    return templates.TemplateResponse("layout_tool.html", {
        "request": request, "static_content": content, "config": cfg
    })

# --- معالجة الأدوات ---
@app.post("/api/webp")
async def api_webp(file: UploadFile = File(...)):
    data = await file.read()
    res = ToolEngine.convert_webp(data)
    return Response(content=res, media_type="image/webp")

@app.post("/api/qr")
async def api_qr(text: str = Form(...)):
    res = ToolEngine.generate_qr(text)
    return Response(content=res, media_type="image/png")

# --- لوحة التحكم الحقيقية ---

@app.get("/system/admin", response_class=HTMLResponse)
async def admin_dash(request: Request, user: str = Depends(admin_auth)):
    tools = list(tools_col.find())
    config = get_config()
    return templates.TemplateResponse("layout_admin.html", {
        "request": request, "tools": tools, "config": config
    })

@app.post("/system/admin/settings")
async def save_settings(
    site_name: str = Form(...),
    site_desc: str = Form(...),
    contact_email: str = Form(...),
    head_code: str = Form(""),
    adsense_code: str = Form(""),
    user: str = Depends(admin_auth)
):
    update_config({
        "site_name": site_name,
        "site_description": site_desc,
        "contact_email": contact_email,
        "head_code": head_code,
        "adsense_code": adsense_code
    })
    return RedirectResponse("/system/admin", status_code=303)

@app.post("/system/admin/tool/edit")
async def edit_tool(
    slug: str = Form(...),
    title: str = Form(...),
    desc: str = Form(...),
    seo: str = Form(...),
    guide: str = Form(...),
    user: str = Depends(admin_auth)
):
    tools_col.update_one(
        {"slug": slug},
        {"$set": {"title": title, "short_desc": desc, "seo_content": seo, "guide": guide}}
    )
    return RedirectResponse("/system/admin", status_code=303)
