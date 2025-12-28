# frontend.py
# V11: Enterprise Magazine Structure (Mega Footer + Static Pages)

# 1. الصفحة الرئيسية (مع الفوتر الضخم)
HOME_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>

<link rel="preconnect" href="https://images.weserv.nl" crossorigin>

    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TRAFICOON | Enterprise Traffic Intelligence</title>
    <link rel="icon" type="image/png" href="https://b.top4top.io/p_3649zxju10.png">
    <meta name="description" content="Leading source for technology analysis, secure distribution protocols, and financial insights.">
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&family=Merriweather:ital@0;1&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; background-color: #f8fafc; color: #0f172a; }
        .serif { font-family: 'Merriweather', serif; }
        .mono { font-family: 'JetBrains Mono', monospace; }
        .btn-shine { position: relative; overflow: hidden; }
        .btn-shine::after { content: ''; position: absolute; top: 0; left: -100%; width: 50%; height: 100%; background: linear-gradient(to right, rgba(255,255,255,0) 0%, rgba(255,255,255,0.3) 50%, rgba(255,255,255,0) 100%); transform: skewX(-25deg); animation: shine 3s infinite; }
        @keyframes shine { 100% { left: 200%; } }
        .card-hover:hover { transform: translateY(-4px); box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); }        
       .line-clamp-3 { display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }


@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.animate-fade-in { animation: fadeIn 0.5s ease-out forwards; }



       
    </style>
   
</head>
<body class="antialiased flex flex-col min-h-screen">

    <nav class="bg-white/90 backdrop-blur border-b border-slate-200 sticky top-0 z-40">
        <div class="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">

       <button onclick="openSidebar()" class="md:hidden text-slate-900 p-2 -ml-2 hover:bg-slate-100 rounded-lg transition">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
            </button>


        
            <a href="/" class="flex items-center gap-3 group">
                <img src="https://b.top4top.io/p_3649zxju10.png" alt="TRAFICOON" class="h-9 w-auto object-contain transition group-hover:scale-105">
                <span class="font-black text-xl tracking-tighter text-slate-900 hidden md:block">TRAFICOON<span class="text-blue-600">.</span></span>
            </a>
            <div class="hidden md:flex gap-6 text-sm font-medium text-slate-600">
                <a href="/" class="hover:text-blue-600 transition">Latest</a>
                {% for niche in niches %}
                <a href="/?category={{ niche }}" class="hover:text-blue-600 transition capitalize">{{ niche }}</a>
                {% endfor %}
            </div>
            <button onclick="openModal()" class="btn-shine bg-slate-900 text-white px-5 py-2.5 rounded-lg text-xs font-bold uppercase tracking-widest hover:bg-slate-800 transition">Client Access</button>
        </div>
    </nav>

    <main class="flex-grow max-w-7xl mx-auto px-6 py-12 w-full">
        <div class="mb-12 text-center border-b border-slate-200 pb-8">
            <span class="text-blue-600 font-bold text-[10px] uppercase tracking-widest bg-blue-50 px-3 py-1 rounded-full">Daily Insights</span>
            <h1 class="text-4xl md:text-5xl font-black text-slate-900 mt-4 mb-3 tracking-tight">Global Market Intelligence</h1>
            <p class="text-slate-500 max-w-2xl mx-auto">Expert analysis on Finance, Technology, and Health trends shaping our future.</p>
        </div>

        {% if articles %}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {% for art in articles %}
           
            <article class="article-item {% if loop.index > 3 %}hidden{% endif %} bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden transition duration-300 card-hover flex flex-col h-full">
                <a href="/read/{{ art._id }}" class="block h-52 overflow-hidden relative group">
                    {% if art.image %}
                    
                    <img src="https://images.weserv.nl/?url={{ art.image }}&w=650&q=80&output=webp" alt="{{ art.title }}" class="w-full h-full object-cover transition duration-700 group-hover:scale-110" loading="lazy">
                    {% else %}
                    <div class="w-full h-full bg-slate-100 flex items-center justify-center text-slate-300">
                        <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                    </div>
                    {% endif %}
                    <span class="absolute top-4 left-4 bg-white/95 backdrop-blur px-3 py-1 text-[10px] font-bold uppercase tracking-widest rounded-full text-blue-600 shadow-sm">{{ art.category|default('General') }}</span>
                </a>
                <div class="p-6 flex-grow flex flex-col">
                    <h2 class="text-lg font-bold text-slate-900 mb-3 leading-tight hover:text-blue-600 transition"><a href="/read/{{ art._id }}">{{ art.title }}</a></h2>
                    <p class="text-slate-500 text-sm mb-4 line-clamp-3 serif flex-grow leading-relaxed">{{ art.meta_desc }}</p>
                    <div class="pt-4 border-t border-slate-50 flex items-center justify-between text-xs text-slate-400 font-medium">
                        <span>{{ art.created_at.strftime('%Y-%m-%d') if art.created_at else 'Today' }}</span>
                        <a href="/read/{{ art._id }}" class="text-blue-600 font-bold hover:underline">Read Report →</a>
                    </div>
                </div>
            </article>
            {% endfor %}
        </div>
<div id="loadMoreBtn" class="mt-12 text-center {% if articles|length <= 3 %}hidden{% endif %}">
            <button onclick="showMoreArticles()" class="group px-8 py-3 border border-slate-300 text-slate-500 font-bold text-xs uppercase tracking-widest rounded-full hover:border-blue-600 hover:text-blue-600 hover:bg-white transition-all duration-300">
                Load More <span class="inline-block transition-transform group-hover:translate-y-0.5">↓</span>
            </button>
        </div>
        
        {% else %}
        <div class="text-center py-20 bg-white rounded-3xl border border-dashed border-slate-200">
            <h3 class="text-lg font-bold text-slate-900">System Initializing...</h3>
            <p class="text-slate-500 mt-2">Content distribution network is syncing.</p>
        </div>
        {% endif %}
    </main>

    <footer class="bg-slate-900 text-slate-300 py-16 border-t border-slate-800">
        <div class="max-w-7xl mx-auto px-6 grid grid-cols-1 md:grid-cols-4 gap-12">
            <div>
                <div class="flex items-center gap-2 mb-6">
                    <img src="https://b.top4top.io/p_3649zxju10.png" class="h-8 w-auto invert opacity-80">
                    <span class="font-black text-xl text-white tracking-tighter">TRAFICOON<span class="text-blue-500">.</span></span>
                </div>
                <p class="text-slate-400 text-sm leading-relaxed mb-6">
                    A global digital media powerhouse delivering cutting-edge analysis in finance, technology, and health sectors.
                </p>
                <div class="flex gap-4">
                    <a href="#" class="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center hover:bg-blue-600 transition"><svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24"><path d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z"/></svg></a>
                    <a href="#" class="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center hover:bg-blue-600 transition"><svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg></a>
                </div>
            </div>

            <div>
                <h4 class="text-white font-bold uppercase tracking-widest text-xs mb-6">Distribution</h4>
                <ul class="space-y-4 text-sm">
                    <li><a href="/?category=tech" class="hover:text-blue-500 transition">Technology</a></li>
                    <li><a href="/?category=finance" class="hover:text-blue-500 transition">Finance & Markets</a></li>
                    <li><a href="/?category=health" class="hover:text-blue-500 transition">Health Science</a></li>
                    <li><a href="/" class="hover:text-blue-500 transition">Latest Reports</a></li>
                </ul>
            </div>

            <div>
                <h4 class="text-white font-bold uppercase tracking-widest text-xs mb-6">Company</h4>
                <ul class="space-y-4 text-sm">
                    <li><a href="/p/about" class="hover:text-blue-500 transition">About Us</a></li>
                    <li><a href="/p/contact" class="hover:text-blue-500 transition">Contact Support</a></li>
                    <li><a href="/p/privacy" class="hover:text-blue-500 transition">Privacy Policy</a></li>
                    <li><a href="/p/terms" class="hover:text-blue-500 transition">Terms of Service</a></li>
                </ul>
            </div>

            <div>
                <h4 class="text-white font-bold uppercase tracking-widest text-xs mb-6">Subscribe</h4>
                <p class="text-xs text-slate-500 mb-4">Get the latest market intelligence delivered to your inbox.</p>
                <div class="flex gap-2">
                    <input placeholder="Enter email" class="bg-slate-800 border border-slate-700 text-white text-xs p-3 rounded-lg w-full outline-none focus:border-blue-500">
                    <button class="bg-blue-600 text-white px-4 rounded-lg font-bold text-xs hover:bg-blue-500">JOIN</button>
                </div>
            </div>
        </div>
        <div class="max-w-7xl mx-auto px-6 pt-12 mt-12 border-t border-slate-800 text-center text-xs text-slate-600">
            © 2025 TRAFICOON Media Inc. All Global Rights Reserved.
        </div>
    </footer>

    <div id="modalBackdrop" class="hidden fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 transition-opacity duration-300">
        <div id="modalContent" class="bg-white w-full max-w-md rounded-2xl shadow-2xl overflow-hidden transform scale-95 transition-transform duration-300 border border-slate-100">
            <div class="bg-slate-50 p-6 border-b border-slate-100 flex justify-between items-center relative">
                <img src="https://b.top4top.io/p_3649zxju10.png" class="h-8 w-auto">
                <button onclick="closeModal()" class="text-slate-400 hover:text-red-500 transition"><svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg></button>
                <div id="scannerLine" class="hidden absolute top-0 left-0 h-1 w-full bg-blue-500 animate-pulse"></div>
            </div>
            <div class="p-8">
                <div id="stepForm">
                    <h2 class="text-xl font-black text-slate-900 mb-2">Secure Link Sanitizer</h2>
                    <p class="text-slate-500 text-xs mb-6">Create a whitened, tracking-safe link for your campaigns.</p>
                    <form id="cleanForm" onsubmit="generateLink(event)" class="space-y-4">
                        <div>
                            <label class="text-[10px] font-bold text-slate-400 uppercase tracking-widest block mb-1">Target URL</label>
                            <input name="target_url" type="url" required class="w-full p-4 bg-slate-50 border border-slate-200 rounded-xl text-sm outline-none focus:border-blue-500" placeholder="https://">
                        </div>
                        <div>
                            <label class="text-[10px] font-bold text-slate-400 uppercase tracking-widest block mb-1">Context Niche</label>
                            <select name="category" class="w-full p-4 bg-slate-50 border border-slate-200 rounded-xl text-sm outline-none focus:border-blue-500">
                                {% for niche in niches %}
                                <option value="{{ niche }}">{{ niche|upper }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        <button class="btn-shine w-full bg-blue-600 text-white py-4 rounded-xl font-bold text-sm uppercase shadow-lg">Generate Secure Link</button>
                    </form>
                </div>
                <div id="stepResult" class="hidden text-center">
                    <h3 class="font-bold text-green-600 mb-2">Link Ready</h3>
                    <div id="finalLinkContainer" class="bg-slate-50 p-4 rounded-xl border border-slate-200 text-xs font-mono text-blue-600 break-all"></div>
                    <button onclick="resetModal()" class="text-xs text-slate-400 mt-4 underline">Create Another</button>
                </div>
            </div>
        </div>
    </div>



<div id="sidebarBackdrop" onclick="closeSidebar()" class="fixed inset-0 bg-slate-900/50 z-50 hidden transition-opacity opacity-0 backdrop-blur-sm"></div>
    
    <div id="sidebarDrawer" class="fixed top-0 left-0 h-full w-80 bg-white shadow-2xl z-50 transform -translate-x-full transition-transform duration-300 ease-in-out overflow-y-auto">
        
        <div class="p-6 border-b border-slate-100 flex justify-between items-center">
            <div class="flex items-center gap-2">
                <img src="https://b.top4top.io/p_3649zxju10.png" class="h-8 w-auto">
                <span class="font-black text-lg text-slate-900">MENU</span>
            </div>
            <button onclick="closeSidebar()" class="text-slate-400 hover:text-red-500 transition p-2 bg-slate-50 rounded-full">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
            </button>
        </div>

        <div class="p-6 space-y-8">
            <div>
                <h4 class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-4">Markets & Sectors</h4>
                <div class="space-y-3 flex flex-col">
                    {% for niche in niches %}
                    <a href="/?category={{ niche }}" class="text-slate-700 font-bold text-sm hover:text-blue-600 hover:bg-blue-50 p-2 rounded-lg transition capitalize flex items-center gap-3">
                        <span class="w-2 h-2 rounded-full bg-blue-600"></span> {{ niche }}
                    </a>
                    {% endfor %}
                    <a href="/" class="text-slate-700 font-bold text-sm hover:text-blue-600 hover:bg-blue-50 p-2 rounded-lg transition flex items-center gap-3">
                        <span class="w-2 h-2 rounded-full bg-slate-300"></span> Latest Reports
                    </a>
                </div>
            </div>

            <div>
                <h4 class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-4">Corporate</h4>
                <div class="space-y-3 flex flex-col text-sm font-medium text-slate-600">
                    <a href="/p/about" class="hover:text-blue-600 transition">About Us</a>
                    <a href="/p/contact" class="hover:text-blue-600 transition">Contact Support</a>
                    <a href="/p/privacy" class="hover:text-blue-600 transition">Privacy Policy</a>
                    <a href="/p/terms" class="hover:text-blue-600 transition">Terms of Service</a>
                </div>
            </div>

            <div class="pt-6 border-t border-slate-100">
                <button onclick="openModal(); closeSidebar()" class="w-full bg-slate-900 text-white py-3 rounded-xl font-bold text-xs uppercase tracking-widest shadow-lg">Client Access</button>
            </div>
        </div>
    </div>





    

    <script>


    

// SIDEBAR LOGIC
        const sidebar = document.getElementById('sidebarDrawer');
        const sbBackdrop = document.getElementById('sidebarBackdrop');

        function openSidebar() {
            sbBackdrop.classList.remove('hidden');
            setTimeout(() => sbBackdrop.classList.remove('opacity-0'), 10);
            sidebar.classList.remove('-translate-x-full');
        }

        function closeSidebar() {
            sidebar.classList.add('-translate-x-full');
            sbBackdrop.classList.add('opacity-0');
            setTimeout(() => sbBackdrop.classList.add('hidden'), 300);
        }





    
        const backdrop = document.getElementById('modalBackdrop');
        const content = document.getElementById('modalContent');
        function openModal() { backdrop.classList.remove('hidden'); setTimeout(() => { content.classList.remove('scale-95'); content.classList.add('scale-100'); }, 10); }
        function closeModal() { content.classList.remove('scale-100'); content.classList.add('scale-95'); setTimeout(() => { backdrop.classList.add('hidden'); resetModal(); }, 300); }
        function resetModal() { document.getElementById('stepForm').classList.remove('hidden'); document.getElementById('stepResult').classList.add('hidden'); document.getElementById('cleanForm').reset(); }
        async function generateLink(e) {
            e.preventDefault(); const form = e.target; const formData = new FormData(form);
            try {
                const res = await fetch('/public/shorten', { method: 'POST', body: formData });
                const html = await res.text();
                const parser = new DOMParser(); const doc = parser.parseFromString(html, 'text/html');
                const link = doc.querySelector('input').value;
                document.getElementById('stepForm').classList.add('hidden');
                document.getElementById('stepResult').classList.remove('hidden');
                document.getElementById('finalLinkContainer').innerHTML = `<input value="${link}" class="bg-transparent w-full outline-none" readonly onclick="this.select()">`;
            } catch(e) { alert('Error'); }
        }


function showMoreArticles() {
            // نختار كل المقالات المخفية
            const hiddenArticles = document.querySelectorAll('.article-item.hidden');
            
            // نظهر أول 3 منها فقط
            for (let i = 0; i < 3; i++) {
                if (hiddenArticles[i]) {
                    hiddenArticles[i].classList.remove('hidden');
                    // إضافة أنيميشن بسيط للظهور
                    hiddenArticles[i].classList.add('animate-fade-in'); 
                }
            }

            // إذا لم يتبق مقالات مخفية، نخفي الزر
            if (document.querySelectorAll('.article-item.hidden').length === 0) {
                document.getElementById('loadMoreBtn').classList.add('hidden');
            }
        }




        
    </script>






                    
                    
            






    
</body>
</html>
"""

# 2. قالب الصفحات الثابتة (Privacy, Terms, About)
PAGE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} | TRAFICOON Media</title>
    <link rel="icon" type="image/png" href="https://b.top4top.io/p_3649zxju10.png">
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=Merriweather:ital@0;1&display=swap" rel="stylesheet">
    <style> body { font-family: 'Inter', sans-serif; background: #f8fafc; } .prose h2 { font-weight: 800; margin-top: 2rem; margin-bottom: 1rem; } .prose p { margin-bottom: 1rem; line-height: 1.7; color: #475569; } </style>
</head>
<body class="flex flex-col min-h-screen">
    <nav class="bg-white border-b border-slate-200 sticky top-0 z-40">
        <div class="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
            <a href="/" class="flex items-center gap-2">
                <img src="https://b.top4top.io/p_3649zxju10.png" class="h-8">
                <span class="font-black text-xl text-slate-900">TRAFICOON<span class="text-blue-600">.</span></span>
            </a>
            <a href="/" class="text-sm font-bold text-slate-500 hover:text-blue-600">Back Home</a>
        </div>
    </nav>

    <main class="flex-grow max-w-4xl mx-auto px-6 py-12 w-full">
        <h1 class="text-4xl font-black text-slate-900 mb-8 tracking-tight">{{ title }}</h1>
        <div class="bg-white p-8 rounded-2xl border border-slate-200 shadow-sm prose">
            {{ content|safe }}
        </div>
    </main>

    <footer class="bg-slate-900 text-slate-400 py-12 text-center text-sm border-t border-slate-800">
        <div class="mb-4 flex justify-center gap-6 font-bold text-xs uppercase tracking-widest">
            <a href="/p/privacy" class="hover:text-white">Privacy</a>
            <a href="/p/terms" class="hover:text-white">Terms</a>
            <a href="/p/contact" class="hover:text-white">Contact</a>
        </div>
        <p>© 2025 TRAFICOON Media Inc.</p>
    </footer>
</body>
</html>
"""
