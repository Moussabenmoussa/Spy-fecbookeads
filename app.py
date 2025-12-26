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

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ad Spy DZ – Professional</title>

<style>
body{
    margin:0;
    font-family:Segoe UI, Tahoma;
    background:#0f1220;
    color:#e5e7eb;
}
.container{
    max-width:1100px;
    margin:auto;
    padding:25px;
}
header{
    display:flex;
    justify-content:space-between;
    align-items:center;
    margin-bottom:25px;
}
.logo{
    font-size:22px;
    font-weight:bold;
    color:#22c55e;
}
.badge{
    background:#1f2937;
    padding:6px 12px;
    border-radius:6px;
    font-size:13px;
    color:#9ca3af;
}
.panel{
    background:#111827;
    border-radius:12px;
    padding:20px;
    margin-bottom:20px;
    box-shadow:0 10px 30px rgba(0,0,0,.4);
}
.search-row{
    display:flex;
    gap:10px;
    flex-wrap:wrap;
}
.search-row input,
.search-row select{
    flex:1;
    padding:12px;
    border-radius:8px;
    border:none;
    background:#1f2937;
    color:#e5e7eb;
    font-size:15px;
}
.search-row button{
    padding:12px 22px;
    border:none;
    border-radius:8px;
    background:#22c55e;
    color:#000;
    font-weight:bold;
    cursor:pointer;
}
.categories{
    display:flex;
    gap:10px;
    flex-wrap:wrap;
    margin-top:15px;
}
.categories button{
    background:#1f2937;
    color:#e5e7eb;
    border:none;
    padding:10px 18px;
    border-radius:8px;
    cursor:pointer;
}
.categories button:hover{
    background:#2563eb;
}
.loader{
    display:none;
    margin:30px auto;
    border:5px solid #1f2937;
    border-top:5px solid #22c55e;
    border-radius:50%;
    width:45px;
    height:45px;
    animation:spin 1s linear infinite;
}
@keyframes spin{100%{transform:rotate(360deg)}}
#status{
    text-align:center;
    margin-top:10px;
    color:#22c55e;
}
.card{
    background:#020617;
    border:1px solid #1f2937;
    padding:18px;
    border-radius:12px;
    display:flex;
    justify-content:space-between;
    align-items:center;
    margin-bottom:12px;
}
.card span{
    color:#9ca3af;
    font-size:14px;
}
.card a{
    background:#2563eb;
    color:white;
    padding:8px 16px;
    border-radius:6px;
    text-decoration:none;
    font-weight:bold;
}
.card a:hover{
    background:#1d4ed8;
}
footer{
    text-align:center;
    margin-top:30px;
    font-size:13px;
    color:#6b7280;
}
</style>
</head>

<body>
<div class="container">

<header>
    <div class="logo">🕵️ Ad Spy DZ</div>
    <div class="badge">META ADS • DZ MARKET</div>
</header>

<div class="panel">
    <div class="search-row">
        <input id="keywordInput" placeholder="🔍 كلمة مفتاحية (مثال: Cuisine, Offre, Montre)">
        <select id="typeFilter">
            <option>الكل</option>
            <option>COD</option>
            <option>عرض</option>
            <option>خصم</option>
        </select>
        <select>
            <option>10 نتائج</option>
            <option>20 نتائج</option>
            <option>50 نتائج</option>
        </select>
        <button onclick="searchKeyword()">بحث</button>
    </div>

    <div class="categories">
        <button onclick="scan('home')">🏠 Home</button>
        <button onclick="scan('beauty')">💄 Beauty</button>
        <button onclick="scan('tech')">📱 Tech</button>
        <button onclick="scan('kids')">👶 Kids</button>
        <button onclick="scan('fashion')">👗 Fashion</button>
        <button onclick="scan('sports')">🏋️ Sports</button>
        <button onclick="scan('food')">🍔 Food</button>
    </div>
</div>

<div class="loader" id="loader"></div>
<div id="status"></div>
<div id="results"></div>

<footer>
    Ad Spy DZ © 2025 – Internal Intelligence Tool
</footer>

</div>

<script>
async function scan(n){
    loader.style.display='block';
    results.innerHTML='';
    status.innerText='Scanning niche: '+n+' ...';
    const r=await fetch('/get_links?niche='+n);
    const d=await r.json();
    loader.style.display='none';
    if(d.status==='success'){
        status.innerText='Found '+d.count+' winning ads';
        d.links.forEach(l=>{
            results.innerHTML+=`
            <div class="card">
                <span>Ad ID: ${l.id}</span>
                <a target="_blank" href="${l.url}">Open Ad</a>
            </div>`;
        });
    }else status.innerText='No results';
}

async function searchKeyword(){
    const k=keywordInput.value.trim();
    if(!k)return alert('أدخل كلمة');
    loader.style.display='block';
    results.innerHTML='';
    status.innerText='Searching: '+k;
    const r=await fetch('/get_links?niche=home');
    const d=await r.json();
    loader.style.display='none';
    if(d.status==='success'){
        status.innerText='Results for '+k;
        d.links.forEach(l=>{
            results.innerHTML+=`
            <div class="card">
                <span>Ad ID: ${l.id}</span>
                <a target="_blank" href="${l.url}">Open Ad</a>
            </div>`;
        });
    }
}
</script>

</body>
</html>
"""

