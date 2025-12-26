
import os, re
from datetime import datetime
from flask import Flask, jsonify, request, render_template_string
from playwright.sync_api import sync_playwright

app = Flask(__name__)

# --- واجهة التيرمينال مع ميزة التصدير ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DZ Hunter Terminal v3.0 [DATA EDITION]</title>
    <style>
        body { background-color: #0d1117; color: #00ff41; font-family: 'Courier New', Courier, monospace; margin: 0; padding: 20px; font-size: 14px; }
        .container { max-width: 1000px; margin: 0 auto; }
        
        .header { border-bottom: 1px solid #333; padding-bottom: 10px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }
        .title span { color: #00ff41; font-weight: bold; }
        .stats { color: #888; font-size: 12px; }

        .input-line { display: flex; align-items: center; margin-bottom: 20px; }
        .prompt { color: #00ff41; margin-right: 10px; font-weight: bold; }
        input { background: transparent; border: none; color: #fff; font-family: 'Courier New', monospace; font-size: 16px; flex: 1; outline: none; }
        
        .logs { background: #000; border: 1px solid #333; padding: 15px; height: 500px; overflow-y: auto; white-space: pre-wrap; box-shadow: 0 0 15px rgba(0, 255, 65, 0.1); margin-bottom: 20px; }
        
        .log-info { color: #888; }
        .log-fb { color: #4267B2; font-weight: bold; }
        .log-store { color: #f1c40f; font-weight: bold; }
        .log-success { color: #00ff41; }
        .log-error { color: #e74c3c; }
        .log-link { color: #3498db; text-decoration: none; border-bottom: 1px dashed #3498db; margin-left: 10px; }
        
        /* زر التحميل المجاني */
        .btn-download {
            background: #238636; color: white; border: 1px solid rgba(240,246,252,0.1);
            padding: 5px 15px; border-radius: 6px; cursor: pointer; font-family: inherit; font-weight: bold;
            display: none; /* مخفي حتى نجد بيانات */
        }
        .btn-download:hover { background: #2ea043; }

        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #000; }
        ::-webkit-scrollbar-thumb { background: #333; }
    </style>
</head>
<body>

<div class="container">
    <div class="header">
        <div class="title">DZ HUNTER <span>TERMINAL</span> [v3.0]</div>
        <button id="downloadBtn" class="btn-download" onclick="exportData()">⬇ DOWNLOAD DATABASE (.CSV)</button>
    </div>

    <div class="logs" id="console">
        <div class="log-info">> System initialized...</div>
        <div class="log-info">> Storage module loaded. Ready to collect data.</div>
        <div class="log-info">> Waiting for command...</div>
    </div>

    <div class="input-line">
        <span class="prompt">root@hunter:~$</span>
        <input type="text" id="commandInput" placeholder="Enter keyword (e.g. 'montre')..." autocomplete="off">
    </div>
</div>

<script>
    const input = document.getElementById('commandInput');
    const consoleDiv = document.getElementById('console');
    const downloadBtn = document.getElementById('downloadBtn');
    
    // مخزن البيانات المؤقت (في المتصفح)
    let COLLECTED_DATA = [];

    function log(msg, type = 'info') {
        const line = document.createElement('div');
        const timestamp = new Date().toLocaleTimeString('en-US', {hour12: false});
        line.className = `log-${type}`;
        line.innerHTML = `<span style="color:#444">[${timestamp}]</span> ${msg}`;
        consoleDiv.appendChild(line);
        consoleDiv.scrollTop = consoleDiv.scrollHeight;
    }

    input.addEventListener("keypress", async function(event) {
        if (event.key === "Enter") {
            const keyword = input.value.trim();
            if (!keyword) return;

            input.value = "";
            input.disabled = true;

            log(`Starting hybrid scan for: "${keyword}"`, 'info');
            log(`> Phase 1: Facebook Ads Library (ID Extraction)...`, 'info');

            try {
                const response = await fetch(`/scan?q=${keyword}`);
                const data = await response.json();

                // FB Results
                if (data.fb_data && data.fb_data.length > 0) {
                    log(`> [FACEBOOK] Found ${data.fb_data.length} ads.`, 'fb');
                    data.fb_data.forEach(ad => {
                        log(`  [AD] ID: ${ad.id} | <a href="${ad.url}" target="_blank" class="log-link">VIEW AD</a>`, 'fb');
                        // تخزين للداتا
                        COLLECTED_DATA.push({
                            Type: "Facebook Ad",
                            Keyword: keyword,
                            Title_ID: ad.id,
                            Link: ad.url,
                            Date_Found: new Date().toLocaleDateString()
                        });
                    });
                } else {
                    log(`> [FACEBOOK] No ads found.`, 'error');
                }

                log(`> Phase 2: Competitor Stores (Google)...`, 'info');
                
                // Store Results
                if (data.store_data && data.store_data.length > 0) {
                    log(`> [STORES] Found ${data.store_data.length} stores.`, 'store');
                    data.store_data.forEach(store => {
                        log(`  [SHOP] ${store.title}`, 'store');
                        log(`         Link: <a href="${store.link}" target="_blank" class="log-link">${store.link}</a>`, 'info');
                        // تخزين للداتا
                        COLLECTED_DATA.push({
                            Type: "Competitor Store",
                            Keyword: keyword,
                            Title_ID: store.title,
                            Link: store.link,
                            Date_Found: new Date().toLocaleDateString()
                        });
                    });
                } else {
                    log(`> [STORES] No stores found.`, 'error');
                }

                // إظهار زر التحميل إذا وجدنا داتا
                if (COLLECTED_DATA.length > 0) {
                    downloadBtn.style.display = "block";
                    downloadBtn.innerText = `⬇ DOWNLOAD DATABASE (${COLLECTED_DATA.length} Items)`;
                    log(`> Data cached. ${COLLECTED_DATA.length} total items ready for export.`, 'success');
                }
                
                log(`> Scan complete.`, 'success');
                log(`------------------------------------------------`, 'info');

            } catch (err) {
                log(`> [FATAL] Error scanning.`, 'error');
            } finally {
                input.disabled = false;
                input.focus();
            }
        }
    });
    
    // دالة التحميل المجانية (Client-Side CSV Generation)
    function exportData() {
        if (COLLECTED_DATA.length === 0) return;
        
        let csvContent = "data:text/csv;charset=utf-8,\uFEFF"; // UTF-8 BOM for Arabic support
        csvContent += "Type,Keyword,Title/ID,Link,Date Found\n"; // Header

        COLLECTED_DATA.forEach(row => {
            let rowStr = `${row.Type},${row.Keyword},"${row.Title_ID}",${row.Link},${row.Date_Found}`;
            csvContent += rowStr + "\n";
        });

        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", "dz_hunter_data.csv");
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        log(`> [SYSTEM] Database exported successfully to dz_hunter_data.csv`, 'success');
    }

    input.focus();
</script>
</body>
</html>
"""

# --- 1. صياد فيسبوك (خفيف) ---
def hunt_facebook(keyword, page):
    try:
        page.goto(f"https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=DZ&q={keyword}", timeout=45000)
        page.wait_for_timeout(3000)
        raw_ids = page.evaluate("""() => {
            const divs = Array.from(document.querySelectorAll('div'));
            const idTexts = divs.filter(d => d.innerText.includes('ID:') && d.innerText.length < 100);
            return [...new Set(idTexts.map(c => c.innerText))].slice(0, 6);
        }""")
        links = []
        for text in raw_ids:
            match = re.search(r'ID: (\d+)', text)
            if match:
                ad_id = match.group(1)
                links.append({"id": ad_id, "url": f"https://www.facebook.com/ads/library/?id={ad_id}"})
        return links
    except: return []

# --- 2. صياد المتاجر (خفيف) ---
def hunt_stores(keyword, page):
    try:
        # نبحث عن متاجر YouCan أو مواقع DZ
        search_query = f'{keyword} (site:youcan.shop OR site:.dz)'
        page.goto(f"https://www.google.com/search?q={search_query}&num=10&hl=en&tbs=qdr:m", timeout=45000) # فلتر الشهر الماضي
        page.wait_for_timeout(2000)
        stores = page.evaluate("""() => {
            const results = [];
            const items = document.querySelectorAll('.g');
            items.forEach(item => {
                const titleEl = item.querySelector('h3');
                const linkEl = item.querySelector('a');
                if (titleEl && linkEl) {
                    const link = linkEl.href;
                    if (!link.includes('facebook') && !link.includes('google')) {
                        results.push({ title: titleEl.innerText.replace(/,/g, ''), link: link });
                    }
                }
            });
            return results.slice(0, 5);
        }""")
        return stores
    except: return []

# --- المحرك الرئيسي ---
def hybrid_scan(keyword):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu', '--single-process'])
        context = browser.new_context(viewport={'width': 800, 'height': 600})
        page = context.new_page()
        page.route("**/*", lambda r: r.abort() if r.request.resource_type in ["image", "media", "font"] else r.continue_())

        results = { "fb_data": hunt_facebook(keyword, page), "store_data": hunt_stores(keyword, page) }
        browser.close()
        return results

@app.route('/')
def index(): return render_template_string(HTML_TEMPLATE)

@app.route('/scan', methods=['GET'])
def scan_endpoint():
    keyword = request.args.get('q', '')
    if not keyword: return jsonify({"status": "error", "msg": "No keyword"})
    return jsonify(hybrid_scan(keyword))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
