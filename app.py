
import os, re
import google.generativeai as genai
from flask import Flask, jsonify, request, render_template_string
from playwright.sync_api import sync_playwright

app = Flask(__name__)

# --- إعدادات الذكاء الاصطناعي ---
os.environ["GEMINI_API_KEY"] = "AIzaSyDV8pA6K4mFs0vnRwjtEKEdTJyJkUby9IU"
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-2.0-flash ')

# --- واجهة الداشبورد (Clean SaaS Design) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DZ Hunter Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>
        :root { --primary: #2563eb; --bg: #f3f4f6; --card: #ffffff; --text: #1f2937; --accent: #8b5cf6; }
        body { font-family: 'Inter', sans-serif; background-color: var(--bg); color: var(--text); margin: 0; padding: 0; }
        
        .navbar { background: var(--card); border-bottom: 1px solid #e5e7eb; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-weight: 900; font-size: 24px; color: var(--primary); letter-spacing: -1px; }
        .logo span { color: var(--text); }
        
        .container { max-width: 1100px; margin: 40px auto; padding: 0 20px; }
        
        /* Search Box */
        .search-section { text-align: center; margin-bottom: 40px; }
        .search-box { background: var(--card); padding: 10px; border-radius: 50px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); display: inline-flex; width: 100%; max-width: 600px; border: 1px solid #e5e7eb; }
        input { border: none; outline: none; flex: 1; padding: 15px 25px; font-size: 16px; border-radius: 50px; }
        button { background: var(--primary); color: white; border: none; padding: 15px 40px; border-radius: 50px; font-weight: 600; cursor: pointer; transition: 0.2s; }
        button:hover { background: #1d4ed8; transform: translateY(-1px); }
        button:disabled { background: #9ca3af; cursor: not-allowed; }

        /* AI Analysis Box */
        .ai-box { background: linear-gradient(135deg, #fdfbfb 0%, #f4f7f6 100%); border: 2px solid var(--accent); border-radius: 16px; padding: 30px; margin-bottom: 40px; display: none; position: relative; overflow: hidden; }
        .ai-title { color: var(--accent); font-weight: 800; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 15px; display: flex; align-items: center; gap: 10px; }
        .ai-content { line-height: 1.8; white-space: pre-wrap; color: #374151; font-size: 15px; }
        
        /* Grid Layout */
        .grid-container { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 30px; }
        
        /* Cards */
        .section-title { font-weight: 800; font-size: 18px; margin-bottom: 20px; color: #4b5563; display: flex; align-items: center; gap: 8px; }
        
        .card { background: var(--card); border-radius: 12px; padding: 20px; border: 1px solid #f3f4f6; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); transition: transform 0.2s; margin-bottom: 15px; }
        .card:hover { transform: translateY(-3px); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }
        
        .card-header { display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 13px; color: #6b7280; }
        .card-title { font-weight: 700; margin-bottom: 5px; color: var(--text); }
        .card-link { display: block; margin-top: 15px; text-align: center; padding: 10px; border-radius: 8px; font-weight: 600; text-decoration: none; font-size: 14px; }
        
        .fb-card { border-left: 4px solid #1877f2; }
        .fb-link { background: #eff6ff; color: #1877f2; }
        .fb-link:hover { background: #dbeafe; }
        
        .store-card { border-left: 4px solid #f59e0b; }
        .store-link { background: #fffbeb; color: #d97706; }
        .store-link:hover { background: #fef3c7; }

        /* Loader */
        .loader { display: none; margin: 20px auto; width: 40px; height: 40px; border: 4px solid #e5e7eb; border-top: 4px solid var(--primary); border-radius: 50%; animation: spin 1s linear infinite; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        
        .status-msg { text-align: center; color: #6b7280; font-size: 14px; margin-top: 10px; }
    </style>
</head>
<body>

    <div class="navbar">
        <div class="logo">DZ <span>HUNTER</span></div>
        <div style="font-size: 12px; font-weight: 600; color: #10b981; background: #d1fae5; padding: 5px 12px; border-radius: 20px;">● System Online</div>
    </div>

    <div class="container">
        <div class="search-section">
            <h1 style="margin-bottom: 10px; font-size: 28px;">Find Your Next Winner</h1>
            <p style="color: #6b7280; margin-bottom: 30px;">Analyze Facebook Ads & Local Stores with AI Power</p>
            
            <div class="search-box">
                <input type="text" id="keyword" placeholder="Enter product (e.g. montre, cuisine)...">
                <button onclick="startAnalysis()" id="btn">Analyze</button>
            </div>
            <div class="loader" id="loader"></div>
            <div class="status-msg" id="status"></div>
        </div>

        <div id="aiSection" class="ai-box">
            <div class="ai-title">✨ Gemini AI Strategy</div>
            <div class="ai-content" id="aiContent"></div>
        </div>

        <div class="grid-container">
            <div>
                <div class="section-title"><span style="color:#1877f2">●</span> Active Facebook Ads</div>
                <div id="fbResults"></div>
            </div>

            <div>
                <div class="section-title"><span style="color:#f59e0b">●</span> Competitor Stores</div>
                <div id="storeResults"></div>
            </div>
        </div>
    </div>

<script>
    async function startAnalysis() {
        const keyword = document.getElementById('keyword').value;
        if(!keyword) return;

        // Reset UI
        document.getElementById('btn').disabled = true;
        document.getElementById('btn').innerText = "Scanning...";
        document.getElementById('loader').style.display = 'block';
        document.getElementById('status').innerText = "Connecting to Gemini AI & Scraping Data...";
        document.getElementById('aiSection').style.display = 'none';
        document.getElementById('fbResults').innerHTML = '';
        document.getElementById('storeResults').innerHTML = '';

        try {
            const res = await fetch(`/scan_ai?q=${keyword}`);
            const data = await res.json();

            if (data.status === 'success') {
                // 1. Show AI
                document.getElementById('aiSection').style.display = 'block';
                document.getElementById('aiContent').innerText = data.ai_response;

                // 2. Show FB Ads
                if (data.fb_links.length > 0) {
                    data.fb_links.forEach(ad => {
                        document.getElementById('fbResults').innerHTML += `
                            <div class="card fb-card">
                                <div class="card-header">
                                    <span>ID: ${ad.id}</span>
                                    <span style="color:green; font-weight:bold">• Active</span>
                                </div>
                                <div class="card-title">Facebook Ad Campaign</div>
                                <a href="${ad.url}" target="_blank" class="card-link fb-link">View Ad in Library ↗</a>
                            </div>`;
                    });
                } else {
                    document.getElementById('fbResults').innerHTML = '<div style="color:#999; text-align:center">No active ads found.</div>';
                }

                // 3. Show Stores
                if (data.store_links.length > 0) {
                    data.store_links.forEach(store => {
                        document.getElementById('storeResults').innerHTML += `
                            <div class="card store-card">
                                <div class="card-header">
                                    <span>Google Search</span>
                                    <span>Store</span>
                                </div>
                                <div class="card-title">${store.title}</div>
                                <a href="${store.link}" target="_blank" class="card-link store-link">Visit Store ↗</a>
                            </div>`;
                    });
                } else {
                    document.getElementById('storeResults').innerHTML = '<div style="color:#999; text-align:center">No specific stores found.</div>';
                }
                
                document.getElementById('status').innerText = "Analysis Complete ✅";
            } else {
                document.getElementById('status').innerText = "Error: " + data.msg;
            }

        } catch (err) {
            document.getElementById('status').innerText = "Server Error. Please try again.";
        } finally {
            document.getElementById('btn').disabled = false;
            document.getElementById('btn').innerText = "Analyze";
            document.getElementById('loader').style.display = 'none';
        }
    }
</script>
</body>
</html>
"""

# --- الذكاء الاصطناعي ---
def get_ai_strategy(keyword):
    try:
        prompt = f"""
        Act as an expert e-commerce copywriter for the Algerian market.
        Product: '{keyword}'.
        
        Output Structure:
        1. 📢 **Ad Hook (Derja):** (A catchy headline)
        2. 📝 **Ad Body:** (Short persuasive text in Algerian Arabic)
        3. 🎯 **Targeting:** (3 best interests for FB Ads)
        4. 💰 **Price:** (Estimated price range in DZD)
        
        Keep it concise and professional.
        """
        response = model.generate_content(prompt)
        return response.text
    except: return "AI service temporarily unavailable."

# --- البحث الخفيف (Playwright Lite) ---
def hunt_data(keyword):
    fb_links = []
    store_links = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage', '--single-process'])
        context = browser.new_context(viewport={'width': 800, 'height': 600})
        page = context.new_page()
        page.route("**/*", lambda r: r.abort() if r.request.resource_type in ["image", "media", "font"] else r.continue_())

        try:
            # 1. FB
            page.goto(f"https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=DZ&q={keyword}", timeout=40000)
            page.wait_for_timeout(3000)
            raw_fb = page.evaluate("""() => {
                const divs = Array.from(document.querySelectorAll('div'));
                const texts = divs.filter(d => d.innerText.includes('ID:') && d.innerText.length < 100);
                return [...new Set(texts.map(t => t.innerText))].slice(0, 5);
            }""")
            for t in raw_fb:
                m = re.search(r'ID: (\d+)', t)
                if m: fb_links.append({"id": m.group(1), "url": f"https://www.facebook.com/ads/library/?id={m.group(1)}"})
            
            # 2. Stores
            page.goto(f"https://www.google.com/search?q={keyword} site:youcan.shop&num=5", timeout=40000)
            raw_stores = page.evaluate("""() => {
                const res = [];
                document.querySelectorAll('.g').forEach(i => {
                    const t = i.querySelector('h3')?.innerText;
                    const l = i.querySelector('a')?.href;
                    if(t && l) res.push({title: t, link: l});
                });
                return res.slice(0, 4);
            }""")
            store_links = raw_stores
            
        except: pass
        finally: browser.close()
        
    return fb_links, store_links

@app.route('/')
def index(): return render_template_string(HTML_TEMPLATE)

@app.route('/scan_ai', methods=['GET'])
def scan_ai():
    q = request.args.get('q', '')
    if not q: return jsonify({"status": "error", "msg": "No keyword"})
    
    # تشغيل العمليات
    ai_res = get_ai_strategy(q)
    fb, stores = hunt_data(q)
    
    return jsonify({
        "status": "success",
        "ai_response": ai_res,
        "fb_links": fb,
        "store_links": stores
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
