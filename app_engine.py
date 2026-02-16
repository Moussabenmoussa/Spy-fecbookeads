import os
from fastapi import FastAPI, Request, Form, File, UploadFile, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from datetime import datetime
from bson import ObjectId

from core_db import PLATFORM_SETTINGS, tools_registry, get_interaction_count
from tool_logic import AuraServices

app = FastAPI(title=PLATFORM_SETTINGS["brand_name"])
templates = Jinja2Templates(directory="templates")
security = HTTPBasic()

# --- Security Dependency ---
def admin_gate(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != PLATFORM_SETTINGS["admin_user"] or \
       credentials.password != PLATFORM_SETTINGS["admin_pass"]:
        raise HTTPException(status_code=401, detail="Secure Access Only")
    return credentials.username

# --- Public Endpoints ---

@app.get("/", response_class=HTMLResponse)
async def home_portal(request: Request):
    all_tools = list(tools_registry.find())
    return templates.TemplateResponse("layout_tool.html", {
        "request": request,
        "config": PLATFORM_SETTINGS,
        "tools_list": all_tools,
        "active": None
    })

@app.get("/tool/{slug}", response_class=HTMLResponse)
async def tool_viewer(request: Request, slug: str):
    tool = tools_registry.find_one({"slug": slug})
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not in registry")
    
    count = get_interaction_count(slug)
    return templates.TemplateResponse("layout_tool.html", {
        "request": request,
        "config": PLATFORM_SETTINGS,
        "active": tool,
        "usage_stat": count
    })

# --- Functional Handlers (The Workhorses) ---

@app.post("/action/webp")
async def action_webp(image: UploadFile = File(...)):
    data = await image.read()
    processed = AuraServices.process_image_webp(data)
    return Response(content=processed, media_type="image/webp", 
                    headers={"Content-Disposition": "attachment; filename=aura_optimized.webp"})

@app.post("/action/qr")
async def action_qr(text: str = Form(...)):
    qr_img = AuraServices.generate_secure_qr(text)
    return Response(content=qr_img, media_type="image/png")

# --- Admin Management ---

@app.get("/system/admin", response_class=HTMLResponse)
async def manage_platform(request: Request, auth: str = Depends(admin_gate)):
    tools = list(tools_registry.find())
    return templates.TemplateResponse("layout_admin.html", {"request": request, "tools": tools})

@app.post("/system/tool/save")
async def save_tool_seo(
    id_str: str = Form(""),
    slug: str = Form(...),
    title: str = Form(...),
    seo_content: str = Form(...), # المحتوى الضخم الذي ستجلبه من Gemini للقبول
    guide: str = Form(...),
    auth: str = Depends(admin_gate)
):
    payload = {
        "slug": slug,
        "title": title,
        "content_html": seo_content,
        "guide_text": guide,
        "last_sync": datetime.utcnow()
    }
    if id_str:
        tools_registry.update_one({"_id": ObjectId(id_str)}, {"$set": payload})
    else:
        tools_registry.insert_one(payload)
    return RedirectResponse(url="/system/admin", status_code=303)

# --- Technical Compliance (The AdSense Trio) ---

@app.get("/sitemap.xml")
async def engine_sitemap():
    tools = tools_registry.find()
    base = f"https://{PLATFORM_SETTINGS['base_domain']}"
    xml = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    xml += f'<url><loc>{base}/</loc></url>'
    for t in tools:
        xml += f'<url><loc>{base}/tool/{t["slug"]}</loc></url>'
    xml += '</urlset>'
    return Response(content=xml, media_type="application/xml")

@app.get("/ads.txt")
async def ads_manifest():
    if not PLATFORM_SETTINGS["adsense_pub_id"]: return Response(content="")
    line = f"google.com, {PLATFORM_SETTINGS['adsense_pub_id']}, DIRECT, f08c47fec0942fa0"
    return Response(content=line, media_type="text/plain")

@app.get("/robots.txt")
async def robots_policy():
    base = f"https://{PLATFORM_SETTINGS['base_domain']}"
    content = f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml"
    return Response(content=content, media_type="text/plain")
