
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Spy Ad Tool 🔗</title>
<style>
body {
    font-family: 'Segoe UI', sans-serif;
    background: #1e1e2f;
    color: #eee;
    margin: 0;
    padding: 20px;
}
.container {
    max-width: 900px;
    margin: 0 auto;
}
h1 {
    text-align: center;
    font-size: 2rem;
    margin-bottom: 10px;
    color: #42b72a;
}
p {
    text-align: center;
    color: #aaa;
    margin-bottom: 20px;
}
.input-group {
    display: flex;
    justify-content: center;
    margin-bottom: 20px;
}
input[type="text"] {
    padding: 10px 15px;
    width: 60%;
    border-radius: 8px 0 0 8px;
    border: none;
    font-size: 16px;
    outline: none;
}
button.search-btn {
    padding: 10px 20px;
    background: #42b72a;
    color: white;
    border: none;
    border-radius: 0 8px 8px 0;
    cursor: pointer;
    font-size: 16px;
}
.categories {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    margin-bottom: 20px;
}
.btn-main {
    background: #1877f2;
    color: white;
    padding: 12px 25px;
    border: none;
    border-radius: 8px;
    font-size: 16px;
    cursor: pointer;
    margin: 5px;
    transition: 0.3s;
}
.btn-main:hover {
    background: #0f5bb5;
}
.loader {
    display: none;
    margin: 20px auto;
    border: 4px solid #333;
    border-top: 4px solid #42b72a;
    border-radius: 50%;
    width: 35px;
    height: 35px;
    animation: spin 1s linear infinite;
}
@keyframes spin {
    0% {transform: rotate(0deg);}
    100% {transform: rotate(360deg);}
}
#results {
    margin-top: 20px;
}
.card {
    background: #2e2e3e;
    padding: 20px;
    margin: 15px 0;
    border-radius: 10px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.5);
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.link-btn {
    text-decoration: none;
    background: #42b72a;
    color: white;
    padding: 10px 20px;
    border-radius: 5px;
    font-weight: bold;
    transition: 0.3s;
}
.link-btn:hover {
    background: #2e8b2e;
}
.id-text {
    color: #aaa;
    font-size: 14px;
}
#status {
    font-weight: bold;
    color: #42b72a;
    margin-bottom: 10px;
    text-align: center;
}
</style>
</head>
<body>
<div class="container">
    <h1>Spy Ad Tool 🔗</h1>
    <p>اختر المجال أو ابحث بالكلمة المفتاحية للحصول على الإعلانات الرابحة</p>
    
    <div class="input-group">
        <input type="text" id="keywordInput" placeholder="أدخل كلمة مفتاحية...">
        <button class="search-btn" onclick="searchKeyword()">بحث</button>
    </div>

    <div class="categories">
        <button onclick="scan('home')" class="btn-main">🏠 منزل</button>
        <button onclick="scan('beauty')" class="btn-main">💄 تجميل</button>
        <button onclick="scan('tech')" class="btn-main">📱 تقنية</button>
        <button onclick="scan('kids')" class="btn-main">👶 أطفال</button>
        <button onclick="scan('fashion')" class="btn-main">👗 أزياء</button>
        <button onclick="scan('sports')" class="btn-main">🏋️ رياضة</button>
        <button onclick="scan('food')" class="btn-main">🍔 أكل</button>
    </div>

    <div class="loader" id="loader"></div>
    <div id="status"></div>
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
                    <a href="${link.url}" target="_blank" class="link-btn">فتح الإعلان</a>
                </div>`;
            });
        } else { s.innerText = "⚠️ لم يتم العثور على روابط، حاول مرة أخرى."; }
    } catch(e) { s.innerText = "❌ خطأ في الاتصال"; }
    finally { document.getElementById('loader').style.display='none'; }
}

async function searchKeyword() {
    const keyword = document.getElementById('keywordInput').value.trim();
    if(!keyword) return alert("أدخل كلمة مفتاحية للبحث!");
    document.getElementById('loader').style.display='block';
    document.getElementById('results').innerHTML='';
    const s = document.getElementById('status');
    s.innerText = `جاري البحث عن: ${keyword}...`;

    try {
        const res = await fetch(`/get_links?niche=custom&keyword=${encodeURIComponent(keyword)}`);
        const data = await res.json();
        if(data.status==='success'){
            s.innerHTML = `✅ تم العثور على ${data.count} إعلانات (الكلمة: ${data.keyword})`;
            data.links.forEach(link => {
                document.getElementById('results').innerHTML += `
                <div class="card">
                    <span class="id-text">ID: ${link.id}</span>
                    <a href="${link.url}" target="_blank" class="link-btn">فتح الإعلان</a>
                </div>`;
            });
        } else { s.innerText = "⚠️ لم يتم العثور على روابط، حاول كلمة أخرى."; }
    } catch(e){ s.innerText = "❌ خطأ في الاتصال"; }
    finally { document.getElementById('loader').style.display='none'; }
}
</script>
</body>
</html>
"""
