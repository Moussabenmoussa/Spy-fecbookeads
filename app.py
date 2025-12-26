import os, re, random
from flask import Flask, jsonify, request, render_template_string
from playwright.sync_api import sync_playwright

app = Flask(__name__)

# =========================
# NICHES
# =========================
NICHES = {
    "home": ["Cuisine", "Maison", "Nettoyage", "Décoration", "Outil"],
    "beauty": ["Soins", "Visage", "Cheveux", "Beauté", "Parfum"],
    "tech": ["Montre", "Écouteurs", "Bluetooth", "Chargeur", "Gadget"],
    "kids": ["Jouet", "Bébé", "Enfant", "Éducatif", "Jeu"]
}

# =========================
# HTML TEMPLATE
# =========================
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<title>Ad Winner Scanner v3</title>
<style>
body{font-family:Segoe UI;background:#f0f2f5;padding:20px;text-align:center}
.container{max-width:850px;margin:auto}
.btn-main{background:#1877f2;color:#fff;padding:12px 25px;border:none;border-radius:8px;margin:5px;cursor:pointer}
.card{background:#fff;padding:15px;margin:10px 0;border-radius:10px;box-shadow:0 2px 5px rgba(0,0,0,.1)}
.link-btn{background:#42b72a;color:#fff;padding:8px 15px;border-radius:5px;text-decoration:none}
.id-text{color:#444;font-size:14px;margin-bottom:5px}
.loader{display:none;margin:20px auto;border:4px solid #f3f3f3;border-top:4px solid #1877f2;border-radius:50%;width:30px;height:30px;animation:spin 1s linear infinite}
@keyframes spin{100%{transform:rotate(360deg)}}
</style>
</head>
<body>
<div class="container">
<h2>🔥 كاشف الإعلانات الرابحة – v3</h2>

<button onclick="scan('home')" class="btn-main">🏠 منزل</button>
<button onclick="scan('beauty')" class="btn-main">💄 تجميل</button>
<button onclick="scan('tech')" class="btn-main">📱 تقنية</button>
<button onclick="scan('kids')" class="btn-main">👶 أطفال</button>

<div class="loader" id="loader"></div>
<div id="status"></div>
<div id="results"></div>
</div>

<script>
async function scan(n){
    document.getElementById('loader').style.display='block';
    document.getElementById('results').innerHTML='';
    document.getElementById('status').innerText='⏳ جاري التحليل الذكي...';

    const res = await fetch('/get_links?niche='+n);
    const data = await res.json();

    document.getElementById('loader').style.display='none';

    if(data.status==='success'){
        document.getElementById('status').innerText =
        `✅ ${data.count} إعلان قوي (كلمة: ${data.keyword})`;

        data.links.forEach(l=>{
            document.getElementById('results').innerHTML += `
            <div class="card">
              <div class="id-text">
                ID: ${l.id} | Score: ${l.score} | Days: ${l.days} | Comments: ${l.comments} | COD: ${l.cod}
              </div>
              <a href="${l.url}" target="_blank" class="link-btn">فتح الإعلان</a>
            </div>`;
        });
    } else {
        document.getElementById('status').innerText='❌ لا توجد نتائج';
    }
}
</script>
</body>
</html>
"""

# =========================
# WINNER INTELLIGENCE v3
# =========================
def get_direct_links(keyword):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--single-process"
            ]
        )

        context = browser.new_context()
        page = context.new_page()

        page.route("**/*", lambda r:
            r.abort() if r.request.resource_type in
            ["image", "media", "font", "stylesheet"]
            else r.continue_()
        )

        try:
            page.goto(
                f"https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=DZ&q={keyword}",
                timeout=60000
            )
            page.wait_for_timeout(8000)

            ads = page.evaluate("""() => {
                const cards = document.querySelectorAll('[data-testid="ad-library-card"]');
                const results = [];

                const SALE_WORDS = [
                    'cod','livraison','gratuit','garantie',
                    'الدفع عند الاستلام','توصيل','عرض','خصم'
                ];

                const CTA_WORDS = [
                    'commandez','acheter','order','shop',
                    'اطلب','سارع','احجز'
                ];

                cards.forEach(card => {
                    const text = card.innerText || '';
                    if (!text.includes('ID:') || !text.includes('Started running')) return;

                    const idm = text.match(/ID:\\s*(\\d+)/);
                    if (!idm) return;

                    // Days running
                    let days = 0;
                    const dm = text.match(/Started running.*?(\\d+)?\\s*(day|week|month)/i);
                    if (dm) {
                        if (dm[2].includes('week')) days = parseInt(dm[1]) * 7;
                        else if (dm[2].includes('month')) days = parseInt(dm[1]) * 30;
                        else days = parseInt(dm[1]);
                    }

                    // Comments
                    let comments = 0;
                    const cm = text.match(/(\\d+)\\s+comment/i);
                    if (cm) comments = parseInt(cm[1]);

                    const copyLen = text.length;
                    const hasCTA = CTA_WORDS.some(w => text.toLowerCase().includes(w));
                    const hasSaleWords = SALE_WORDS.some(w => text.toLowerCase().includes(w));

                    let score = 0;

                    if (days >= 7) score += 25;
                    if (days >= 14) score += 50;
                    if (days >= 30) score += 90;

                    score += Math.floor(comments / 10) * 15;

                    if (copyLen > 120) score += 20;
                    if (copyLen > 200) score += 35;

                    if (hasCTA) score += 20;
                    if (hasSaleWords) score += 30;

                    if (comments < 5 && days < 7) return;
                    if (copyLen < 60) return;

                    if (score >= 80) {
                        results.push({
                            id: idm[1],
                            score,
                            days,
                            comments,
                            cod: hasSaleWords
                        });
                    }
                });

                return results;
            }""")

            links = [{
                "id": ad["id"],
                "url": f"https://www.facebook.com/ads/library/?id={ad['id']}",
                "score": ad["score"],
                "days": ad["days"],
                "comments": ad["comments"],
                "cod": ad["cod"]
            } for ad in ads]

            links.sort(key=lambda x: x["score"], reverse=True)
            return links[:10]

        except Exception:
            return []
        finally:
            browser.close()

# =========================
# ROUTES
# =========================
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/get_links')
def get_links():
    niche = request.args.get('niche', 'home')
    keyword = random.choice(NICHES.get(niche, NICHES['home']))

    links = get_direct_links(keyword)
    if links:
        return jsonify({
            "status": "success",
            "count": len(links),
            "keyword": keyword,
            "links": links
        })
    return jsonify({"status": "empty"})

# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
