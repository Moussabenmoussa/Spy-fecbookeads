import os
import uvicorn
from fastapi import FastAPI, Request, HTTPException, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime

# Import Modules
from database import db
import seo_utils

# --- CONFIG ---
app = FastAPI()
templates = Jinja2Templates(directory="templates")
ADMIN_PASSWORD = os.environ.get("SECRET_KEY", "admin123")

# Connect DB
@app.on_event("startup")
def startup_db_client():
    db.connect()

# --- MODELS ---
class ProjectCreate(BaseModel):
    name: str
    slug: str # e.g. 'iptv-guide'
    domain_url: str # Your money site
    google_verification: str

class PageData(BaseModel):
    project_id: str
    keyword: str
    variables: Dict[str, Any] # { "device": "Samsung", "country": "UK" }
    status: str = "draft" # draft, published

# --- ROUTES: ADMIN ---

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

@app.post("/api/projects")
async def create_project(project: ProjectCreate, password: str = Form(...)):
    if password != ADMIN_PASSWORD: raise HTTPException(403)
    res = db.get_collection("projects").insert_one(project.dict())
    return {"message": "Project Created", "id": str(res.inserted_id)}

@app.get("/api/projects")
async def get_projects(password: str):
    if password != ADMIN_PASSWORD: raise HTTPException(403)
    projects = list(db.get_collection("projects").find({}, {"_id": 0}))
    return projects

@app.post("/api/generate-batch")
async def generate_batch(
    password: str = Form(...), 
    project_slug: str = Form(...), 
    template: str = Form(...),
    data_rows: str = Form(...) # JSON string of rows
):
    """
    The Core Engine: Takes template + data rows and generates pages
    """
    if password != ADMIN_PASSWORD: raise HTTPException(403)
    
    rows = json.loads(data_rows)
    generated_count = 0
    
    project = db.get_collection("projects").find_one({"slug": project_slug})
    if not project: raise HTTPException(404, "Project not found")

    for row in rows:
        # 1. Create unique slug
        page_slug = f"{row['device']}-in-{row['country']}".lower().replace(" ", "-")
        
        # 2. Check if exists
        exists = db.get_collection("pages").find_one({"slug": page_slug, "project_slug": project_slug})
        if exists: continue

        # 3. Generate AI Content (Intro)
        ai_intro = seo_utils.generate_ai_content(
            prompt=f"Intro for article about IPTV on {row['device']} in {row['country']}",
            context="Technical, helpful, mention 4K"
        )

        # 4. Save Page
        page_doc = {
            "project_slug": project_slug,
            "slug": page_slug,
            "title": template.replace("{{device}}", row['device']).replace("{{country}}", row['country']),
            "variables": row,
            "ai_content": ai_intro,
            "status": "published", # Or scheduled
            "created_at": datetime.now()
        }
        db.get_collection("pages").insert_one(page_doc)
        generated_count += 1

    return {"message": f"Successfully generated {generated_count} pages."}

# --- ROUTES: PUBLIC (SEO PAGES) ---

@app.get("/p/{project_slug}/{page_slug}", response_class=HTMLResponse)
async def view_page(request: Request, project_slug: str, page_slug: str):
    # 1. Get Project Settings
    project = db.get_collection("projects").find_one({"slug": project_slug})
    if not project: raise HTTPException(404)

    # 2. Get Page Data
    page = db.get_collection("pages").find_one({"slug": page_slug, "project_slug": project_slug})
    if not page: raise HTTPException(404)

    # 3. Render Template (Simple for now, can be dynamic later)
    # We inject variables into a base HTML structure
    return templates.TemplateResponse("generated_page.html", {
        "request": request,
        "page": page,
        "project": project,
        "meta_verify": project.get("google_verification", "")
    })

@app.get("/img/{page_slug}.png")
async def dynamic_image(page_slug: str):
    """Generates OG Image on the fly"""
    page = db.get_collection("pages").find_one({"slug": page_slug})
    if not page: raise HTTPException(404)
    
    img_io = seo_utils.generate_og_image(page['title'])
    return StreamingResponse(img_io, media_type="image/png")

@app.get("/sitemap/{project_slug}.xml")
async def sitemap(request: Request, project_slug: str):
    base_url = str(request.base_url).rstrip("/")
    pages = list(db.get_collection("pages").find({"project_slug": project_slug}))
    
    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for p in pages:
        xml.append(f'<url><loc>{base_url}/p/{project_slug}/{p["slug"]}</loc><changefreq>weekly</changefreq></url>')
    xml.append('</urlset>')
    
    return Response(content="".join(xml), media_type="application/xml")

import json # Helper import

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
