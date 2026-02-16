import json
import os
from functools import lru_cache
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from groq import Groq

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Load Groq
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

with open('data.json', 'r') as f:
    DATA = json.load(f)

# --- GENERATE COMBINATIONS ---
def get_all_combinations():
    combos = []
    
    # 1. Setup Guides: Device + Country
    for device in DATA['devices']:
        for country in DATA['countries']:
            slug = f"setup-iptv-on-{device['slug']}-in-{country['slug']}"
            combos.append({
                "type": "setup",
                "slug": slug,
                "device": device,
                "country": country,
                "title": f"How to Setup IPTV on {device['name']} in {country['name']} (2026)"
            })

    # 2. Watch Guides: Interest + Device
    for interest in DATA['interests']:
        for device in DATA['devices']:
            slug = f"watch-{interest['slug']}-on-{device['slug']}"
            combos.append({
                "type": "watch",
                "slug": slug,
                "device": device,
                "interest": interest,
                "title": f"How to Watch {interest['name']} on {device['name']} (Buffer-Free)"
            })
            
    return combos

COMBINATIONS = get_all_combinations()
SLUG_MAP = {item['slug']: item for item in COMBINATIONS}

# --- AI GENERATOR ---
@lru_cache(maxsize=1000)
def generate_ai_intro(title: str, context: str):
    if not client: return f"Comprehensive guide: {title}. {context}"
    try:
        prompt = f"Write a short, engaging 50-word intro for a blog post titled '{title}'. Context: {context}. Tone: Expert & Helpful."
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7, max_tokens=100
        )
        return completion.choices[0].message.content.strip()
    except: return f"Welcome to the ultimate guide for {title}."

# --- ROUTES ---
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request, "combinations": COMBINATIONS, "total": len(COMBINATIONS)
    })

@app.get("/sitemap.xml")
async def sitemap(request: Request):
    base_url = str(request.base_url).rstrip("/")
    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    xml.append(f'<url><loc>{base_url}/</loc><changefreq>daily</changefreq><priority>1.0</priority></url>')
    for item in COMBINATIONS:
        xml.append(f'<url><loc>{base_url}/{item["slug"]}</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>')
    xml.append('</urlset>')
    return Response(content="".join(xml), media_type="application/xml")

@app.get("/{slug}", response_class=HTMLResponse)
async def article_page(request: Request, slug: str):
    data_item = SLUG_MAP.get(slug)
    if not data_item: raise HTTPException(404, "Page not found")
    
    # Context for AI
    if data_item['type'] == 'setup':
        ctx = f"Setting up IPTV in {data_item['country']['name']} on {data_item['device']['name']}."
    else:
        ctx = f"Streaming {data_item['interest']['name']} on {data_item['device']['name']}."

    ai_intro = generate_ai_intro(data_item['title'], ctx)
    
    return templates.TemplateResponse("article.html", {
        "request": request,
        "item": data_item,
        "main_store_url": DATA['main_store_url'],
        "ai_intro": ai_intro
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
