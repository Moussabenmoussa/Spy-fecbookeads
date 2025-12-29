# HTML Templates stored as strings for simplicity

# 1. الصفحة الرئيسية (Home)
HOME_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TRAFICOON | Global Market Intelligence</title>
    <meta name="description" content="Expert analysis on Finance, Technology, and Health trends shaping our future.">
    
    <link rel="preconnect" href="https://images.weserv.nl" crossorigin>
    
    <script src="https://cdn.tailwindcss.com"></script>
    
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
        .line-clamp-2 { display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
    </style>
</head>
<body class="bg-slate-50 text-slate-800">

    <nav class="bg-white/90 backdrop-blur border-b border-slate-200 sticky top-0 z-40">
        <div class="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
            
            <div class="flex items-center gap-2">
                <button onclick="openSidebar()" aria-label="Open Menu" class="md:hidden text-slate-700 p-2 -ml-2 hover:bg-slate-100 rounded-lg transition">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
                </button>
                <a href="/" class="flex items-center gap-2 group">
                    <img src="https://b.top4top.io/p_3649zxju10.png" alt="TRAFICOON" class="h-8 w-auto object-contain transition group-hover:scale-105">
                    <span class="font-black text-xl tracking-tighter text-slate-900">TRAFICOON<span class="text-blue-600">.</span></span>
                </a>
            </div>

            <div class="hidden md:flex items-center gap-8 text-sm font-bold text-slate-600">
                {% for niche in niches %}
                <a href="/?category={{ niche }}" class="hover:text-blue-600 transition capitalize">{{ niche }}</a>
                {% endfor %}
                <button onclick="openModal()" class="bg-slate-900 text-white px-6 py-2.5 rounded-full hover:bg-slate-800 transition">Client Access</button>
            </div>
        </div>
    </nav>

    <header class="py-16 px-6 text-center bg-white border-b border-slate-200">
        <div class="max-w-3xl mx-auto space-y-4">
            <span class="inline-block py-1 px-3 rounded-full bg-blue-50 text-blue-600 text-xs font-black tracking-widest uppercase">Daily Insights</span>
            <h1 class="text-5xl md:text-6xl font-black text-slate-900 tracking-tight">Global Market <br> <span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">Intelligence</span></h1>
            <p class="text-lg text-slate-500 font-medium leading-relaxed">Expert analysis on Finance, Technology, and Health trends shaping our future.</p>
        </div>
    </header>

    <main class="max-w-7xl mx-auto px-6 py-12">
        
        <div id="articles-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-x-8 gap-y-12">
            {% for art in articles %}
            <article class="group cursor-pointer flex flex-col h-full">
                <a href="/p/{{ art._id }}" class="block overflow-hidden rounded-2xl mb-4 relative aspect-[16/10] shadow-sm">
                    <span class="absolute top-4 left-4 z-10 bg-white/90 backdrop-blur px-3 py-1 rounded-md text-[10px] font-black uppercase tracking-wider text-slate-800 shadow-sm">{{ art.category }}</span>
                    <img src="https://images.weserv.nl/?url={{ art.image }}&w=650&q=80&output=webp" 
                         width="650" height="400" 
                         alt="{{ art.title }}" 
                         class="w-full h-full object-cover transition duration-700 group-hover:scale-110" 
                         loading="lazy"
                         decoding="async">
                </a>
                <div class="flex-1 flex flex-col">
                    <h2 class="text-xl font-bold text-slate-900 mb-2 leading-tight group-hover:text-blue-600 transition line-clamp-2">
                        <a href="/p/{{ art._id }}">{{ art.title }}</a>
                    </h2>
                    <div class="text-slate-400 text-xs font-medium uppercase tracking-widest mt-auto">
                        Read Analysis &rarr;
                    </div>
                </div>
            </article>
            {% endfor %}
        </div>

        {% if has_next %}
        <div class="mt-16 text-center">
            <button id="loadMoreBtn" data-page="{{ page }}" onclick="loadMore()" class="group relative inline-flex items-center justify-center px-8 py-3 font-bold text-white transition-all duration-200 bg-slate-900 font-pj rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-slate-900 hover:bg-slate-800">
                Load More Reports
                <svg class="w-5 h-5 ml-2 transition-transform duration-200 group-hover:translate-y-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
            </button>
        </div>
        {% endif %}

    </main>

    <footer class="bg-white border-t border-slate-200 py-12 mt-12">
        <div class="max-w-7xl mx-auto px-6 text-center">
            <img src="https://b.top4top.io/p_3649zxju10.png" class="h-8 mx-auto mb-6 opacity-50 grayscale">
            <p class="text-slate-400 text-sm mb-6">© 2025 Traficoon Inc. All rights reserved.</p>
            <div class="flex justify-center gap-6 text-xs font-bold text-slate-500 uppercase tracking-widest">
                <a href="#" class="hover:text-slate-900">Privacy</a>
                <a href="#" class="hover:text-slate-900">Terms</a>
                <a href="#" class="hover:text-slate-900">Contact</a>
            </div>
        </div>
    </footer>

    <div id="sidebarBackdrop" onclick="closeSidebar()" class="fixed inset-0 bg-slate-900/50 z-50 hidden transition-opacity opacity-0 backdrop-blur-sm"></div>
    <div id="sidebarDrawer" class="fixed top-0 left-0 h-full w-80 bg-white shadow-2xl z-50 transform -translate-x-full transition-transform duration-300 ease-in-out overflow-y-auto">
        <div class="p-6 border-b border-slate-100 flex justify-between items-center">
            <div class="flex items-center gap-2">
                <img src="https://b.top4top.io/p_3649zxju10.png" class="h-8 w-auto">
                <span class="font-black text-lg text-slate-900">MENU</span>
            </div>
            <button onclick="closeSidebar()" aria-label="Close Menu" class="text-slate-400 hover:text-red-500 transition p-2 bg-slate-50 rounded-full">
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
                    <a href="#" class="hover:text-blue-600 transition">About Us</a>
                    <a href="#" class="hover:text-blue-600 transition">Contact Support</a>
                    <a href="#" class="hover:text-blue-600 transition">Privacy Policy</a>
                    <a href="#" class="hover:text-blue-600 transition">Terms of Service</a>
                </div>
            </div>

            <div class="pt-6 border-t border-slate-100">
                <button onclick="openModal(); closeSidebar()" class="w-full bg-slate-900 text-white py-3 rounded-xl font-bold text-xs uppercase tracking-widest shadow-lg">Client Access</button>
            </div>
        </div>
    </div>

    <script>
        // Sidebar Logic
        const sidebar = document.getElementById('sidebarDrawer');
        const backdrop = document.getElementById('sidebarBackdrop');

        function openSidebar() {
            backdrop.classList.remove('hidden');
            setTimeout(() => { backdrop.classList.remove('opacity-0'); }, 10);
            sidebar.classList.remove('-translate-x-full');
        }

        function closeSidebar() {
            backdrop.classList.add('opacity-0');
            sidebar.classList.add('-translate-x-full');
            setTimeout(() => { backdrop.classList.add('hidden'); }, 300);
        }

        function openModal() { alert("Access Restricted to Premium Clients."); }

        // AJAX Load More Logic
        let isLoading = false;
        function loadMore() {
            if(isLoading) return;
            isLoading = true;
            const btn = document.getElementById('loadMoreBtn');
            let page = parseInt(btn.getAttribute('data-page'));
            
            btn.innerHTML = 'Loading...';
            
            fetch(`/?page=${page + 1}`, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(response => response.text())
            .then(html => {
                if(html.trim()) {
                    document.getElementById('articles-grid').insertAdjacentHTML('beforeend', html);
                    btn.setAttribute('data-page', page + 1);
                    btn.innerHTML = 'Load More Reports <svg class="w-5 h-5 ml-2 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>';
                } else {
                    btn.style.display = 'none';
                }
                isLoading = false;
            })
            .catch(() => {
                isLoading = false;
                btn.innerHTML = 'Error. Try Again.';
            });
        }
    </script>
</body>
</html>
"""

# 2. صفحة المقال (Article Page)
ARTICLE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ article.title }}</title>
    
    <link rel="preconnect" href="https://images.weserv.nl" crossorigin>
    
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap" rel="stylesheet">
    <style>body { font-family: 'Inter', sans-serif; }</style>
</head>
<body class="bg-white text-slate-800">

    <nav class="border-b border-slate-100 h-16 flex items-center justify-center sticky top-0 bg-white/95 backdrop-blur z-50">
        <a href="/" class="flex items-center gap-2">
            <img src="https://b.top4top.io/p_3649zxju10.png" class="h-6 w-auto">
            <span class="font-black text-lg text-slate-900 tracking-tighter">TRAFICOON</span>
        </a>
    </nav>

    <div class="fixed top-0 left-0 h-1 bg-blue-600 z-[60]" id="progressBar" style="width: 0%"></div>

    <main class="max-w-4xl mx-auto px-6 py-12">
        
        <span class="text-blue-600 font-bold tracking-widest uppercase text-xs mb-4 block">{{ article.category }}</span>
        <h1 class="text-3xl md:text-5xl font-black text-slate-900 mb-8 leading-tight">{{ article.title }}</h1>
        
        <article class="prose prose-lg prose-slate max-w-none">
            {{ article.content | safe }}
        </article>

        <div class="mt-16 p-8 bg-slate-50 rounded-2xl border-l-4 border-blue-600">
            <p class="text-xs font-black text-slate-400 uppercase tracking-widest mb-2">Don't Miss</p>
            <div class="grid gap-4">
                {% for r in related %}
                <a href="/p/{{ r._id }}" class="group block">
                    <h3 class="font-bold text-slate-800 group-hover:text-blue-600 transition text-lg">{{ r.title }}</h3>
                </a>
                {% endfor %}
            </div>
        </div>

        <div class="mt-12 text-center">
            <a href="/" class="inline-flex items-center text-sm font-bold text-slate-400 hover:text-slate-900 transition">
                &larr; Back to Market Intelligence
            </a>
        </div>

    </main>

    <script>
        // Scroll Progress
        window.onscroll = function() {
            var winScroll = document.body.scrollTop || document.documentElement.scrollTop;
            var height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            var scrolled = (winScroll / height) * 100;
            document.getElementById("progressBar").style.width = scrolled + "%";
        };
    </script>
</body>
</html>
"""

# 3. جزء الشبكة (لتحميل المزيد - AJAX)
ARTICLES_GRID_HTML = """
{% for art in articles %}
<article class="group cursor-pointer flex flex-col h-full">
    <a href="/p/{{ art._id }}" class="block overflow-hidden rounded-2xl mb-4 relative aspect-[16/10] shadow-sm">
        <span class="absolute top-4 left-4 z-10 bg-white/90 backdrop-blur px-3 py-1 rounded-md text-[10px] font-black uppercase tracking-wider text-slate-800 shadow-sm">{{ art.category }}</span>
        <img src="https://images.weserv.nl/?url={{ art.image }}&w=650&q=80&output=webp" 
             width="650" height="400" 
             alt="{{ art.title }}" 
             class="w-full h-full object-cover transition duration-700 group-hover:scale-110" 
             loading="lazy" decoding="async">
    </a>
    <div class="flex-1 flex flex-col">
        <h2 class="text-xl font-bold text-slate-900 mb-2 leading-tight group-hover:text-blue-600 transition line-clamp-2">
            <a href="/p/{{ art._id }}">{{ art.title }}</a>
        </h2>
        <div class="text-slate-400 text-xs font-medium uppercase tracking-widest mt-auto">
            Read Analysis &rarr;
        </div>
    </div>
</article>
{% endfor %}
"""
