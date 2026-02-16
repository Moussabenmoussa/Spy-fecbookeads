import json
import os
from functools import lru_cache
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from groq import Groq

# --- CONFIG ---
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Load Groq
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Load Data Matrix
with open('data.json', 'r') as f:
    DATA = json.load(f)

# --- HELPER: Generate Permutations ---
def get_all_combinations():
    combos = []
    for device in DATA['devices']:
        for country in DATA['countries']:
            # URL Structure: /iptv-for-{device}-in-{country}
            slug = f"iptv-for-{device['slug']}-in-{country['slug']}"
            combos.append({
                "slug": slug,
                "device": device,
                "country": country,
                "title": f"How to Watch IPTV on {device['name']} in {country['name']} (2026 Guide)"
            })
    return combos

COMBINATIONS = get_all_combinations()
SLUG_MAP = {item['slug']: item for item in COMBINATIONS}

# --- AI GENERATOR (WITH CACHING) ---
@lru_cache(maxsize=500)
def generate_ai_intro(device_name: str, country_name: str):
    """
    Generates a UNIQUE intro for every page to please Google.
    Cached in memory so we don't hit API limits.
    """
    if not client:
        return f"Looking for the best IPTV solution for {device_name} in {country_name}? You are in the right place."
    
    try:
        prompt = f"""
        Write a short, engaging, and unique introduction paragraph (approx 60 words) for a blog post about watching IPTV specifically on '{device_name}' for users living in '{country_name}'. 
        Mention 4K streaming and stability. Do not mention specific prices. 
        Tone: Helpful and technical.
        """
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=100
        )
        return completion.choices[0].message.content.strip()
    except:
        return f"Experience the ultimate 4K streaming on your {device_name}. For viewers in {country_name}, stability is key."

# --- ROUTES ---

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Index of all 192+ pages"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "combinations": COMBINATIONS,
        "total": len(COMBINATIONS)
    })

@app.get("/sitemap.xml")
async def sitemap(request: Request):
    """Auto-generated XML Sitemap"""
    base_url = str(request.base_url).rstrip("/")
    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    
    xml.append(f'<url><loc>{base_url}/</loc><changefreq>daily</changefreq><priority>1.0</priority></url>')
    
    for item in COMBINATIONS:
        xml.append(f'<url><loc>{base_url}/{item["slug"]}</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>')
    
    xml.append('</urlset>')
    return Response(content="".join(xml), media_type="application/xml")

@app.get("/{slug}", response_class=HTMLResponse)
async def article_page(request: Request, slug: str):
    """Dynamic Page with AI Content"""
    data_item = SLUG_MAP.get(slug)
    
    if not data_item:
        raise HTTPException(status_code=404, detail="Guide not found")
    
    # Generate Unique AI Content on the fly
    ai_content = generate_ai_intro(data_item['device']['name'], data_item['country']['name'])
    
    return templates.TemplateResponse("article.html", {
        "request": request,
        "device": data_item['device'],
        "country": data_item['country'],
        "main_store_url": DATA['main_store_url'],
        "title": data_item['title'],
        "ai_intro": ai_content # Injecting AI text
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
