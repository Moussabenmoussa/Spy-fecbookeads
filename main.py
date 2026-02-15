import json
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Setup Templates
templates = Jinja2Templates(directory="templates")

# Load Data
with open('data.json', 'r') as f:
    DATA = json.load(f)

# Helper: Generate all possible combinations
def get_all_combinations():
    combos = []
    for device in DATA['devices']:
        for country in DATA['countries']:
            # Slug Pattern: iptv-for-{device}-in-{country}
            slug = f"iptv-for-{device['slug']}-in-{country['slug']}"
            combos.append({
                "slug": slug,
                "device": device,
                "country": country,
                "title": f"Best IPTV for {device['name']} in {country['name']} (2026 Guide)"
            })
    return combos

COMBINATIONS = get_all_combinations()
SLUG_MAP = {item['slug']: item for item in COMBINATIONS}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Index page listing all generated articles for Google Crawler
    """
    return templates.TemplateResponse("index.html", {
        "request": request,
        "combinations": COMBINATIONS,
        "total": len(COMBINATIONS)
    })

@app.get("/sitemap.xml")
async def sitemap(request: Request):
    """
    Auto-generated Sitemap for SEO
    """
    base_url = str(request.base_url).rstrip("/")
    xml_content = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml_content.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    
    # Add Homepage
    xml_content.append(f'<url><loc>{base_url}/</loc><changefreq>daily</changefreq><priority>1.0</priority></url>')
    
    # Add All Article Pages
    for item in COMBINATIONS:
        xml_content.append(f'<url><loc>{base_url}/{item["slug"]}</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>')
    
    xml_content.append('</urlset>')
    return Response(content="".join(xml_content), media_type="application/xml")

@app.get("/{slug}", response_class=HTMLResponse)
async def article_page(request: Request, slug: str):
    """
    Dynamic Article Generator
    """
    data_item = SLUG_MAP.get(slug)
    
    if not data_item:
        raise HTTPException(status_code=404, detail="Article not found")
    
    return templates.TemplateResponse("article.html", {
        "request": request,
        "device": data_item['device'],
        "country": data_item['country'],
        "main_store_url": DATA['main_store_url'],
        "title": data_item['title']
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
