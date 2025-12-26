import os, re, random
from datetime import datetime
from flask import Flask, jsonify, request, render_template_string
from playwright.sync_api import sync_playwright

app = Flask(__name__)

# --- Terminal UI (Professional Hacker Style) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ad Hunter Terminal v1.0</title>
    <style>
        body {
            background-color: #0d1117;
            color: #00ff41;
            font-family: 'Courier New', Courier, monospace;
            margin: 0;
            padding: 20px;
            font-size: 14px;
        }
        .container { max-width: 900px; margin: 0 auto; }
        
        /* Terminal Header */
        .header {
            border-bottom: 1px solid #333;
            padding-bottom: 10px;
            margin-bottom: 20px;
            color: #fff;
        }
        .header span { color: #00ff41; font-weight: bold; }
        
        /* Input Area */
        .input-line { display: flex; align-items: center; margin-bottom: 20px; }
        .prompt { color: #00ff41; margin-right: 10px; font-weight: bold; }
        input {
            background: transparent;
            border: none;
            color: #fff;
            font-family: 'Courier New', Courier, monospace;
            font-size: 16px;
            flex: 1;
            outline: none;
        }
        
        /* Logs Area */
        .logs {
            background: #000;
            border: 1px solid #333;
            padding: 15px;
            height: 400px;
            overflow-y: auto;
            white-space: pre-wrap;
            box-shadow: 0 0 10px rgba(0, 255, 65, 0.1);
        }
        
        /* Log Colors */
        .log-info { color: #888; }
        .log-success { color: #00ff41; font-weight: bold; }
        .log-warn { color: #f1c40f; }
        .log-error { color: #e74c3c; }
        .log-link { color: #3498db; text-decoration: none; border-bottom: 1px dashed #3498db; }
        .log-link:hover { background: #3498db; color: #000; }

        /* Scrollbar */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #000; }
        ::-webkit-scrollbar-thumb { background: #333; }
    </style>
</head>
<body>

<div class="container">
    <div class="header">
        AD HUNTER <span>TERMINAL</span> [v1.0.0] <br>
        <small style="color:#555">Connected to Server: RENDER-NODE-01 | Latency: 42ms</small>
    </div>

    <div class="logs" id="console">
        <div class="log-info">> System initialized...</div>
        <div class="log-info">> Ready for target keywords.</div>
    </div>

    <div class="input-line">
        <span class="prompt">root@hunter:~$</span>
        <input type="text" id="commandInput" placeholder="Enter keyword (e.g., 'watch', 'kitchen')..." autocomplete="off">
    </div>
</div>

<script>
    const input = document.getElementById('commandInput');
    const consoleDiv = document.getElementById('console');

    function log(msg, type = 'info') {
        const line = document.createElement('div');
        const timestamp = new Date().toLocaleTimeString();
        line.className = `log-${type}`;
        
        // Simulating type effect
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

            log(`Executing search sequence for target: "${keyword}"...`, 'info');
            log(`> Initializing Stealth Mode...`, 'info');
            log(`> Bypassing meta-guards...`, 'info');

            try {
                const response = await fetch(`/scan?q=${keyword}`);
                const data = await response.json();

                if (data.status === "success") {
                    log(`> [SUCCESS] Target acquired. Found ${data.count} candidates.`, 'success');
                    log(`> Filtering low-quality ads (Age < 3 days)...`, 'warn');
                    
                    if (data.results.length === 0) {
                        log(`> [RESULT] No high-value targets found. All ads were too new.`, 'error');
                    } else {
                        data.results.forEach(ad => {
                            log(`------------------------------------------------`, 'info');
                            log(`TARGET ID: ${ad.id}`, 'success');
                            log(`DURATION : ${ad.days_running} Days Active`, 'warn');
                            log(`ACCESS   : <a href="${ad.url}" target="_blank" class="log-link">OPEN SECURE LINK</a>`, 'info');
                        });
                        log(`------------------------------------------------`, 'info');
                        log(`> Operation completed successfully.`, 'success');
                    }
                } else {
                    log(`> [ERROR] ${data.msg}`, 'error');
                }

            } catch (err) {
                log(`> [FATAL] Connection lost or server timeout.`, 'error');
            } finally {
                input.disabled = false;
                input.focus();
            }
        }
    });
    
    // Auto focus
    input.focus();
</script>
</body>
</html>
"""

def analyze_ad(raw_text):
    # 1. Extract ID
    id_match = re.search(r'ID: (\d+)', raw_text)
    ad_id = id_match.group(1) if id_match else None

    # 2. Extract Date
    # Format: "Started running on Nov 25, 2024"
    date_match = re.search(r'Started running on (.*?) Platforms', raw_text)
    days_running = 0
    
    if date_match:
        date_str = date_match.group(1).strip()
        try:
            # Parsing date
            ad_date = datetime.strptime(date_str, "%b %d, %Y")
            days_running = (datetime.now() - ad_date).days
        except:
            days_running = 0 # If parsing fails, treat as new

    return {
        "id": ad_id,
        "days_running": days_running,
        "url": f"https://www.facebook.com/ads/library/?id={ad_id}" if ad_id else "#"
    }

def terminal_hunter(keyword):
    with sync_playwright() as p:
        # Ultra-lightweight browser
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu', '--single-process']
        )
        page = browser.new_context(viewport={'width': 800, 'height': 600}).new_page()
        
        # Block everything except text
        page.route("**/*", lambda route: route.abort() 
            if route.request.resource_type in ["image", "media", "font", "stylesheet"] 
            else route.continue_())

        try:
            # Go to FB Library
            page.goto(f"https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=DZ&q={keyword}", timeout=60000)
            page.wait_for_timeout(5000)

            # Scrape raw text containing dates and IDs
            raw_ads = page.evaluate("""() => {
                const divs = Array.from(document.querySelectorAll('div'));
                // Only get divs that have 'Started running' info
                const cards = divs.filter(d => d.innerText.includes('Started running') && d.innerText.includes('ID:') && d.innerText.length < 500);
                return [...new Set(cards.map(c => c.innerText))].slice(0, 10);
            }""")
            
            cleaned_data = []
            for raw in raw_ads:
                data = analyze_ad(raw)
                # FILTER: Only keep ads running for 3 days or more (Quality Control)
                if data['id'] and data['days_running'] >= 3:
                    cleaned_data.append(data)
            
            return cleaned_data

        except Exception as e:
            return []
        finally:
            browser.close()

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/scan', methods=['GET'])
def scan_endpoint():
    keyword = request.args.get('q', '')
    if not keyword: return jsonify({"status": "error", "msg": "No keyword provided"})
    
    results = terminal_hunter(keyword)
    
    if results:
        return jsonify({
            "status": "success", 
            "count": len(results), 
            "results": results
        })
    else:
        # If no results found or all filtered out
        return jsonify({"status": "success", "count": 0, "results": [], "msg": "No ads passed the quality filter."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
