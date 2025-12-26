
import os, re
from datetime import datetime
from flask import Flask, jsonify, request, render_template_string
from playwright.sync_api import sync_playwright

app = Flask(__name__)

# --- واجهة التيرمينال الاحترافية (Hacker UI) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ad Hunter Terminal v5.0</title>
    <style>
        body { background-color: #0c0c0c; color: #33ff00; font-family: 'Courier New', monospace; margin: 0; padding: 20px; font-size: 14px; }
        .container { max-width: 900px; margin: 0 auto; }
        .header { border-bottom: 2px solid #333; padding-bottom: 15px; margin-bottom: 20px; }
        .title { font-size: 20px; font-weight: bold; letter-spacing: 2px; }
        .subtitle { color: #666; font-size: 12px; }
        
        .input-area { display: flex; align-items: center; background: #111; padding: 12px; border: 1px solid #333; border-radius: 4px; }
        .prompt { color: #33ff00; margin-right: 10px; font-weight: bold; }
        input { background: transparent; border: none; color: #fff; font-family: inherit; font-size: 16px; flex: 1; outline: none; }
        
        .logs { background: #000; border: 1px solid #333; height: 500px; overflow-y: auto; padding: 15px; margin-top: 20px; white-space: pre-wrap; border-radius: 4px; }
        
        .log-sys { color: #555; }
        .log-info { color: #ccc; }
        .log-winner { color: #33ff00; font-weight: bold; text-shadow: 0 0 5px #33ff00; }
        .log-test { color: #f1c40f; }
        .log-link a { color: #00ffff; text-decoration: none; border-bottom: 1px dotted #00ffff; }
        .log-link a:hover { background: #00ffff; color: #000; }

        /* Scrollbar */
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-thumb { background: #333; border-radius: 3px; }
    </style>
</head>
<body>

<div class="container">
    <div class="header">
        <div class="title">DZ_HUNTER_TERMINAL [PRO]</div>
        <div class="subtitle">TARGET: FACEBOOK ADS LIBRARY | STATUS: ONLINE</div>
    </div>
    
    <div class="input-area">
        <span class="prompt">root@hunter:~$</span>
        <input type="text" id="cmd" placeholder="Enter keyword (e.g. montre, cuisine)..." autocomplete="off">
    </div>

    <div class="logs" id="console">
        <div class="log-sys">> System initialized.</div>
        <div class="log-sys">> Smart Analysis Module loaded.</div>
        <div class="log-sys">> Ready for command...</div>
    </div>
</div>

<script>
    const input = document.getElementById('cmd');
    const con = document.getElementById('console');

    function log(msg, type='info') {
        const div = document.createElement('div');
        const time = new Date().toLocaleTimeString('en-US',{hour12:false});
        div.className = `log-${type}`;
        div.innerHTML = `<span style="color:#444">[${time}]</span> ${msg}`;
        con.appendChild(div);
        con.scrollTop = con.scrollHeight;
    }

    input.addEventListener("keypress", async (e) => {
        if (e.key === "Enter") {
            const val = input.value.trim();
            if (!val) return;
            
            input.value = "";
            input.disabled = true;
            log(`Starting scan sequence for: "${val}"`, 'sys');
            log(`> Bypassing security & analyzing ad duration...`, 'info');

            try {
                const res = await fetch(`/analyze?q=${val}`);
                const data = await res.json();
                
                if (data.status === "success") {
                    log(`> [SCAN COMPLETE] Found ${data.count} candidates.`, 'sys');
                    log(`------------------------------------------------`, 'sys');
                    
                    data.results.forEach(ad => {
                        if(ad.is_winner) {
                            log(`[WINNER] 🔥 ACTIVE FOR ${ad.days} DAYS!`, 'winner');
                        } else {
                            log(`[TESTING] 🧪 Active for ${ad.days} days`, 'test');
                        }
                        log(`ID: ${ad.id} | <span class="log-link"><a href="${ad.url}" target="_blank">OPEN AD</a></span>`, 'info');
                        log(`------------------------------------------------`, 'sys');
                    });

                    if(data.count === 0) log(`> No ads found with clear dates. Try another keyword.`, 'info');
                } else {
                    log(`> [ERROR] ${data.msg}`, 'error');
                }
            } catch (err) {
                log(`> [CRITICAL] Server overload. Try again in 10s.`, 'error');
            } finally {
                input.disabled = false;
                input.focus();
            }
        }
    });
    input.focus();
</script>
</body>
</html>
"""

# --- المحرك الذكي (خفيف على الرام + يستخرج التاريخ) ---
def smart_hunter(keyword):
    with sync_playwright() as p:
        # 1. إعدادات قصوى لتوفير الرام (وضع التقشف)
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu', '--single-process']
        )
        # صفحة صغيرة جداً
        page = browser.new_context(viewport={'width': 800, 'height': 600}).new_page()
        
        # 2. حظر صارم للميديا
        page.route("**/*", lambda r: r.abort() if r.request.resource_type in ["image", "media", "font", "stylesheet"] else r.continue_())

        try:
            # 3. الذهاب لفيسبوك
            page.goto(f"https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=DZ&q={keyword}", timeout=50000)
            page.wait_for_timeout(4000)

            # 4. السحر: استخراج النصوص التي تحتوي على التاريخ فقط
            # نبحث عن كروت تحتوي على كلمة "Started" (بالإنجليزية) أو "Lancée" (بالفرنسية)
            raw_data = page.evaluate("""() => {
                const divs = Array.from(document.querySelectorAll('div'));
                // نأخذ فقط العناصر التي فيها تاريخ ومعرف
                const cards = divs.filter(d => 
                    (d.innerText.includes('Started running') || d.innerText.includes('Lancée le')) && 
                    d.innerText.includes('ID:') && 
                    d.innerText.length < 400
                );
                // نأخذ 5 نتائج فقط لنضمن عدم انهيار السيرفر
                return [...new Set(cards.map(c => c.innerText))].slice(0, 5);
            }""")

            results = []
            for text in raw_data:
                # استخراج ID
                id_match = re.search(r'ID: (\d+)', text)
                if not id_match: continue
                ad_id = id_match.group(1)

                # استخراج التاريخ وحساب الأيام
                days_active = 0
                is_winner = False
                
                # محاولة قراءة التاريخ (يدعم الإنجليزية والفرنسية)
                # English pattern: Started running on Nov 25, 2024
                en_match = re.search(r'Started running on (.*?) Platforms', text)
                # French pattern: Lancée le 25 nov. 2024
                fr_match = re.search(r'Lancée le (.*?) Plateformes', text)

                date_str = ""
                if en_match: date_str = en_match.group(1).strip()
                elif fr_match: date_str = fr_match.group(1).strip()

                if date_str:
                    try:
                        # تنظيف بسيط للتاريخ
                        # ملاحظة: التاريخ يعتمد على لغة السيرفر، سنفترض الإنجليزية الافتراضية للتبسيط
                        # في حالة الفشل نعتبره 0
                        ad_date = datetime.strptime(date_str.replace("  ", " "), "%b %d, %Y")
                        days_active = (datetime.now() - ad_date).days
                    except:
                        pass # إذا فشل تحليل التاريخ، يبقى 0
                
                if days_active >= 4: is_winner = True

                results.append({
                    "id": ad_id,
                    "days": days_active,
                    "is_winner": is_winner,
                    "url": f"https://www.facebook.com/ads/library/?id={ad_id}"
                })
            
            # ترتيب النتائج: الرابح أولاً
            results.sort(key=lambda x: x['days'], reverse=True)
            return results

        except Exception as e:
            return []
        finally:
            browser.close()

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/analyze', methods=['GET'])
def analyze_endpoint():
    q = request.args.get('q', '')
    if not q: return jsonify({"status": "error", "msg": "Empty keyword"})
    
    data = smart_hunter(q)
    return jsonify({"status": "success", "count": len(data), "results": data})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
