import os, re, random
from flask import Flask, jsonify, request, render_template_string
from playwright.sync_api import sync_playwright

app = Flask(__name__)

# قوائم الكلمات
NICHES = {
    "home": [
        "Cuisine", "Maison", "Nettoyage", "Décoration", "Outil",
        "Ustensiles", "Décoration intérieure", "Rangement", "Maison pratique",
        "مطبخ DZ", "ديكور DZ", "أدوات منزلية", "تنظيف", "عرض", "خصم", "توصيل"
    ],
    "beauty": [
        "Soins", "Visage", "Cheveux", "Beauté", "Parfum",
        "Makeup", "Cosmétiques", "Shampoing", "Huile cheveux",
        "تجميل DZ", "بشرة", "شعر", "كريمات", "ماسكات", "عرض", "خصم", "توصيل"
    ],
    "tech": [
        "Montre", "Écouteurs", "Bluetooth", "Chargeur", "Gadget",
        "Smartwatch", "Powerbank", "Accessoires téléphones", "Laptop", "Ordinateur",
        "سماعات DZ", "شواحن", "هواتف", "أجهزة", "عرض", "خصم", "توصيل"
    ],
    "kids": [
        "Jouet", "Bébé", "Enfant", "Éducatif", "Jeu",
        "Puzzle", "Figurines", "Coloriage", "Livre enfant", "Jeux éducatifs",
        "ألعاب DZ", "طفل", "رضيع", "تعليمي", "أنشطة للأطفال", "عرض", "خصم", "توصيل"
    ],
    "fashion": [
        "Sac", "Chaussures", "Vêtement", "Homme", "Femme",
        "Shirts", "Pantalon", "Mode", "Bijoux", "Lunettes",
        "حقائب DZ", "أحذية", "ملابس", "رجالي", "نسائي", "عرض", "خصم", "توصيل"
    ],
    "sports": [
        "Sport", "Fitness", "Gym", "Équipement", "Running",
        "Tapis yoga", "Haltères", "Vêtements fitness", "Basket", "Football",
        "رياضة DZ", "تمارين", "جيم", "معدات رياضية", "حذاء رياضي", "عرض", "خصم", "توصيل"
    ],
    "food": [
        "Alimentation", "Snack", "Boisson", "Gâteau", "Pâtisserie",
        "Fast food", "Fruits", "Légumes", "Juice", "Snack healthy",
        "أكل DZ", "حلويات", "معجنات", "مشروبات", "عرض", "خصم", "توصيل"
    ]
}

HTML_TEMPLATE = """<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Direct Ad Links 🔗</title><style>body{font-family:'Segoe UI',sans-serif;background:#f0f2f5;margin:0;padding:20px;text-align:center}.container{max-width:800px;margin:0 auto}.btn-main{background:#1877f2;color:white;padding:12px 25px;border:none;border-radius:8px;font-size:16px;cursor:pointer;margin:5px}.card{background:white;padding:20px;margin:15px 0;border-radius:10px;box-shadow:0 2px 5px rgba(0,0,0,0.1);display:flex;justify-content:between;align-items:center}.link-btn{text-decoration:none;background:#42b72a;color:white;padding:10px 20px;border-radius:5px;font-weight:bold}.id-text{color:#666;font-size:14px}.loader{display:none;margin:20px auto;border:4px solid #f3f3f3;border-top:4px solid #1877f2;border-radius:50%;width:30px;height:30px;animation:spin 1s linear infinite}@keyframes spin{0%{transform:rotate(0deg)}100%{transform:rotate(360deg)}}</style></head><body>
<div class="container">
    <h1>🔗 كاشف روابط الإعلانات</h1>
    <p>اختر المجال وسأعطيك روابط مباشرة للإعلانات الرابحة</p>
    <div>
        <button onclick="scan('home')" class="btn-main">🏠 منزل</button>
        <button onclick="scan('beauty')" class="btn-main">💄 تجميل</button>
        <button onclick="scan('tech')" class="btn-main">📱 تقنية</button>
        <button onclick="scan('kids')" class="btn-main">👶 أطفال</button>
    </div>
    <div class="loader" id="loader"></div>
    <div id="status" style="margin-top:20px;font-weight:bold;color:#555"></div>
    <div id="results"></div>
</div>
<script>
async function scan(n){
    document.getElementById('loader').style.display='block';
    document.getElementById('results').innerHTML='';
    const s = document.getElementById('status');
    s.innerText = `جاري سحب الروابط لقسم: ${n}...`;
    
    try {
        const res = await fetch(`/get_links?niche=${n}`);
        const data = await res.json();
        if(data.status==='success'){
            s.innerHTML = `✅ تم العثور على ${data.count} إعلانات (الكلمة: ${data.keyword})`;
            data.links.forEach(link => {
                document.getElementById('results').innerHTML += `
                <div class="card">
                    <span class="id-text">ID: ${link.id}</span>
                    <a href="${link.url}" target="_blank" class="link-btn">🔗 فتح الإعلان في فيسبوك</a>
                </div>`;
            });
        } else { s.innerText = "⚠️ لم يتم العثور على روابط، حاول مرة أخرى."; }
    } catch(e) { s.innerText = "❌ خطأ في الاتصال"; }
    finally { document.getElementById('loader').style.display='none'; }
}
</script></body></html>"""

def get_direct_links(keyword):
    with sync_playwright() as p:
        # إعدادات قصوى لتوفير الرام
        b = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu', '--single-process']
        )
        # نغلق تحميل كل شيء ما عدا الهيكل الأساسي
        page = b.new_context().new_page()
        page.route("**/*", lambda r: r.abort() if r.request.resource_type in ["image", "media", "font", "stylesheet"] else r.continue_())

        try:
            # نذهب لصفحة البحث
            page.goto(f"https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=DZ&q={keyword}", timeout=60000)
            page.wait_for_timeout(5000)

            # نسحب فقط النصوص التي تحتوي على ID
            raw_ids = page.evaluate("""() => {
                const divs = Array.from(document.querySelectorAll('div'));
                // نبحث عن النص الذي يحتوي على ID فقط
                const idTexts = divs.filter(d => d.innerText.includes('ID:') && d.innerText.length < 100);
                return [...new Set(idTexts.map(c => c.innerText))].slice(0, 10);
            }""")

            links = []
            for text in raw_ids:
                # استخراج الرقم فقط
                match = re.search(r'ID: (\d+)', text)
                if match:
                    ad_id = match.group(1)
                    # صنع الرابط المباشر
                    links.append({
                        "id": ad_id,
                        "url": f"https://www.facebook.com/ads/library/?id={ad_id}"
                    })
            
            return links
        except: return []
        finally: b.close()

@app.route('/')
def index(): return render_template_string(HTML_TEMPLATE)

@app.route('/get_links')
def get_links():
    niche = request.args.get('niche', 'home')
    keyword = random.choice(NICHES.get(niche, NICHES['home']))
    links = get_direct_links(keyword)
    
    if links:
        return jsonify({"status": "success", "count": len(links), "keyword": keyword, "links": links})
    return jsonify({"status": "empty"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

