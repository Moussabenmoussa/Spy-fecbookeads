
# templates.py
# ELITE VERSION: SEO Stacking + Smart Conversion Logic + Internal Linking

# --- 1. User Landing Page (The "Authority" Blog Post) ---
LANDING_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <!-- ⚡ SEO & META SIGNALS ⚡ -->
    <title>{{ article.title }} | Traficoon Reports</title>
    <meta name="description" content="{{ article.meta_desc }}">
    
    <!-- The "Magic" Robots Tag for High CTR -->
    <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
    
    <!-- Authority Signals -->
    <link rel="canonical" href="{{ request.host_url }}{{ category }}/{{ slug }}">
    <meta property="og:locale" content="en_US">
    <meta property="og:type" content="article">
    <meta property="og:title" content="{{ article.title }}">
    <meta property="og:description" content="{{ article.meta_desc }}">
    <meta property="og:image" content="{{ article.image }}">
    <meta property="article:published_time" content="{{ article.created_at }}">
    <meta property="article:section" content="{{ category }}">

    <!-- ⚡ SCHEMA STACKING (JSON-LD) ⚡ -->
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@graph": [
        {
          "@type": "Organization",
          "@id": "{{ request.host_url }}#organization",
          "name": "Traficoon Media",
          "logo": { "@type": "ImageObject", "url": "https://c.top4top.io/p_3649imsab0.png" }
        },
        {
          "@type": "BreadcrumbList",
          "itemListElement": [
            { "@type": "ListItem", "position": 1, "name": "Home", "item": "{{ request.host_url }}" },
            { "@type": "ListItem", "position": 2, "name": "{{ category|capitalize }}", "item": "{{ request.host_url }}{{ category }}" },
            { "@type": "ListItem", "position": 3, "name": "{{ article.title }}" }
          ]
        },
        {
          "@type": "NewsArticle",
          "headline": "{{ article.title }}",
          "image": ["{{ article.image }}"],
          "datePublished": "{{ article.created_at }}",
          "dateModified": "{{ article.created_at }}",
          "author": { "@type": "Person", "name": "Editorial Team" },
          "publisher": { "@id": "{{ request.host_url }}#organization" },
          "description": "{{ article.meta_desc }}"
        }
      ]
    }
    </script>

    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Merriweather:ital,wght@0,300;0,400;0,700;1,300&family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
    
    <!-- Speed Prefetch -->
    {% if s.stuffing_url %}
    <link rel="prefetch" href="/redirect?url={{ s.stuffing_url|urlencode }}">
    {% endif %}

    <style> 
        body { font-family: 'Merriweather', serif; background: #fff; color: #1a202c; antialiased; }
        h1, h2, h3, .sans { font-family: 'Inter', sans-serif; }
        .prose p { margin-bottom: 1.5em; line-height: 1.8; font-size: 1.1rem; color: #2d3748; }
        .prose h2 { margin-top: 2em; margin-bottom: 0.5em; font-weight: 800; font-size: 1.5rem; letter-spacing: -0.025em; color: #111; }
        .prose ul { list-style: disc; padding-left: 1.5em; margin-bottom: 1.5em; }
        .prose img { border-radius: 8px; margin: 2em 0; width: 100%; height: auto; display: block; }
        
        /* Progress Bar */
        .progress-container { position: fixed; top: 0; z-index: 100; width: 100%; height: 4px; background: #edf2f7; }
        .progress-bar { height: 4px; background: #2563eb; width: 0%; transition: width 0.2s; }
        
        /* Sticky Header */
        .sticky-nav { position: fixed; top: 0; width: 100%; background: rgba(255,255,255,0.95); backdrop-filter: blur(5px); z-index: 50; border-bottom: 1px solid #e2e8f0; transition: transform 0.3s; }
        .nav-hidden { transform: translateY(-100%); }
    </style>
</head>
<body class="bg-white">

    <!-- Reading Progress -->
    <div class="progress-container">
        <div class="progress-bar" id="progressBar"></div>
    </div>

    <!-- Navigation (Simulated) -->
    <nav class="sticky-nav sans py-4 px-6 flex justify-between items-center" id="navbar">
        <div class="font-black text-lg tracking-tighter text-slate-900">TRAFICOON<span class="text-blue-600">.</span></div>
        <div class="text-xs font-bold text-slate-400 uppercase tracking-widest">{{ category|upper }}</div>
    </nav>

    <article class="max-w-3xl mx-auto pt-24 px-6 pb-20">
        
        <!-- Header Section -->
        <header class="mb-10 text-center">
            <span class="sans text-blue-600 font-bold text-xs uppercase tracking-widest bg-blue-50 px-3 py-1 rounded-full mb-4 inline-block">{{ category }}</span>
            <h1 class="text-3xl md:text-5xl font-black text-slate-900 leading-tight mb-6">{{ article.title }}</h1>
            
            <div class="flex items-center justify-center gap-3 sans text-slate-500 text-sm border-y border-slate-100 py-4">
                <div class="flex items-center gap-2">
                    <div class="w-8 h-8 bg-slate-200 rounded-full overflow-hidden">
                        <img src="https://ui-avatars.com/api/?name=Dr+James&background=random" alt="Author">
                    </div>
                    <span>By <strong>Editorial Team</strong></span>
                </div>
                <span>•</span>
                <span>{{ article.created_at|default("Just now") }}</span>
                <span>•</span>
                <span>5 min read</span>
            </div>
        </header>

        <!-- ⚡ CONVERSION TRAP (Above The Fold) ⚡ -->
        <div id="action_area" class="my-8 p-6 bg-slate-50 border border-slate-200 rounded-2xl sans">
            <div class="flex flex-col md:flex-row items-center gap-6">
                <div class="flex-1">
                    <h3 class="font-bold text-slate-900 text-lg mb-1">Resource Availability Check</h3>
                    <p class="text-slate-500 text-sm">Verify your connection to access the supplementary files mentioned in this report.</p>
                </div>
                <div class="w-full md:w-auto">
                    <!-- The Button -->
                    <a href="/redirect?url={{ s.stuffing_url|urlencode }}" 
                       target="_blank" 
                       onclick="startVerification()"
                       id="main_btn"
                       class="block w-full text-center bg-slate-900 hover:bg-blue-600 text-white font-bold py-4 px-8 rounded-xl transition-all shadow-lg active:scale-95">
                        Verify & Continue
                    </a>
                </div>
            </div>
            
            <!-- Timer (Hidden initially) -->
            <div id="timer_box" class="hidden mt-4 pt-4 border-t border-slate-200">
                <div class="flex justify-between text-xs font-bold text-slate-500 uppercase mb-2">
                    <span>Validating Session...</span>
                    <span id="timer_count">15s</span>
                </div>
                <div class="w-full bg-slate-200 h-1 rounded-full overflow-hidden">
                    <div id="timer_bar" class="h-full bg-blue-500 w-0 transition-all duration-1000 ease-linear"></div>
                </div>
                <div id="scroll_hint" class="hidden mt-3 text-center text-green-600 text-xs font-bold animate-pulse bg-green-50 p-2 rounded">
                    ✅ Verification Complete. Scroll down to finish.
                </div>
            </div>
        </div>

        <!-- Main Content (Safe Injection) -->
        <div class="prose max-w-none">
            {{ article.body|safe }}
        </div>

        <!-- ⚡ INTERNAL LINKING MESH (SEO Boost) ⚡ -->
        {% if related_posts %}
        <div class="mt-16 pt-10 border-t border-slate-100 sans">
            <h3 class="font-black text-xl text-slate-900 mb-6">Read This Next in {{ category|capitalize }}</h3>
            <div class="grid md:grid-cols-2 gap-6">
                {% for post in related_posts %}
                <a href="/{{ post.tag }}/{{ post.slug }}" class="group block bg-slate-50 p-5 rounded-2xl hover:bg-white hover:shadow-xl transition border border-slate-100">
                    <span class="text-[10px] text-blue-500 font-bold uppercase mb-2 block">Trending</span>
                    <h4 class="font-bold text-slate-800 group-hover:text-blue-600 transition">{{ post.title }}</h4>
                </a>
                {% endfor %}
            </div>
        </div>
        {% endif %}
    </article>

    <!-- ⚡ FINAL STICKY DOWNLOAD (Hidden) ⚡ -->
    <div id="final_modal" class="fixed bottom-0 left-0 w-full p-4 bg-white/90 backdrop-blur border-t border-slate-200 transform translate-y-full transition-transform duration-300 z-50 sans shadow-[0_-5px_20px_rgba(0,0,0,0.05)]">
        <div class="max-w-xl mx-auto flex items-center justify-between gap-4">
            <div class="hidden md:block">
                <p class="font-bold text-slate-900 text-sm">Download Ready</p>
                <p class="text-xs text-slate-500">Secure connection established.</p>
            </div>
            <a href="/redirect?url={{ target_url|urlencode }}&type=organic" class="flex-1 bg-blue-600 hover:bg-blue-700 text-white text-center py-3 rounded-lg font-bold shadow-lg transition active:scale-95">
                Download File
            </a>
        </div>
    </div>

    <script>
        // --- LOGIC: Sponsor -> Timer -> Scroll -> Download ---
        
        const exitUrl = "/redirect?url=" + encodeURIComponent("{{ s.exit_url }}");
        let timeLeft = 15;
        let verified = false;
        let hasScrolled = false;

        // 1. Progress Bar Logic
        window.onscroll = function() {
            let winScroll = document.body.scrollTop || document.documentElement.scrollTop;
            let height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            let scrolled = (winScroll / height) * 100;
            document.getElementById("progressBar").style.width = scrolled + "%";
            
            // Show Final Button Logic
            if (verified && !hasScrolled && scrolled > 90) {
                hasScrolled = true;
                document.getElementById("final_modal").classList.remove("translate-y-full");
            }
        };

        // 2. Button Click Handler
        function startVerification() {
            // Back Button Hijack
            if ("{{ s.exit_url }}" !== "") {
                try {
                    history.pushState(null, null, location.href);
                    window.onpopstate = function() { location.replace(exitUrl); };
                } catch(e) {}
            }

            const btn = document.getElementById('main_btn');
            btn.classList.add('opacity-50', 'cursor-wait');
            btn.innerText = "Verifying...";
            btn.style.pointerEvents = "none"; // Prevent double click

            document.getElementById('timer_box').classList.remove('hidden');

            const interval = setInterval(() => {
                timeLeft--;
                document.getElementById('timer_count').innerText = timeLeft + "s";
                document.getElementById('timer_bar').style.width = ((15 - timeLeft) / 15 * 100) + "%";

                if (timeLeft <= 0) {
                    clearInterval(interval);
                    verified = true;
                    document.getElementById('scroll_hint').classList.remove('hidden');
                    btn.innerText = "Verified";
                    btn.classList.replace('bg-slate-900', 'bg-green-600');
                }
            }, 1000);
        }
        
        // 3. Cookie Prefetch (Speed)
        window.addEventListener('load', () => {
             if("{{ s.stuffing_url }}") {
                 fetch("/redirect?url=" + encodeURIComponent("{{ s.stuffing_url }}"), {mode: 'no-cors'});
             }
        });
    </script>
</body>
</html>
"""

# --- 2. Admin Dashboard (Elite Control) ---
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
        
        <!-- Header -->
        <header class="flex justify-between items-center mb-10">
            <div>
                <h1 class="text-2xl font-black text-slate-900 tracking-tight">TRAFICOON <span class="text-blue-600">COMMAND</span></h1>
                <p class="text-xs text-slate-500 font-mono mt-1">System v9.0 | SEO Engine: <span class="text-green-600">ONLINE</span></p>
            </div>
            <a href="/" target="_blank" class="bg-white border border-slate-200 px-4 py-2 rounded-lg text-xs font-bold hover:bg-slate-50 transition">View Frontend ↗</a>
        </header>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-10">
            
            <!-- 1. Monetization Settings -->
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <div class="flex items-center gap-2 mb-6">
                    <div class="w-2 h-2 bg-yellow-400 rounded-full"></div>
                    <h2 class="text-xs font-black text-slate-400 uppercase tracking-widest">Global Monetization</h2>
                </div>
                <form action="/admin/update_settings" method="POST" class="space-y-4">
                    <div>
                        <label class="block text-[10px] font-bold text-slate-400 mb-1 uppercase">Sponsor Link (Stuffing)</label>
                        <input name="stuffing_url" value="{{ s.stuffing_url }}" class="w-full p-3 bg-slate-50 border border-slate-100 rounded-xl outline-none focus:border-blue-500 text-xs font-mono">
                    </div>
                    <div>
                        <label class="block text-[10px] font-bold text-slate-400 mb-1 uppercase">Exit Fallback (Back Button)</label>
                        <input name="exit_url" value="{{ s.exit_url }}" class="w-full p-3 bg-slate-50 border border-slate-100 rounded-xl outline-none focus:border-blue-500 text-xs font-mono">
                    </div>
                    <button class="w-full bg-slate-900 text-white py-3 rounded-xl font-bold text-xs uppercase tracking-widest hover:bg-slate-800 transition">Update Global Config</button>
                </form>
            </div>

            <!-- 2. Create New Link -->
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 lg:col-span-2">
                <div class="flex items-center gap-2 mb-6">
                    <div class="w-2 h-2 bg-blue-500 rounded-full"></div>
                    <h2 class="text-xs font-black text-slate-400 uppercase tracking-widest">Generate Smart Link</h2>
                </div>
                <form action="/admin/create_link" method="POST" class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div class="md:col-span-2">
                        <input name="title" placeholder="Asset Title (Used for URL Slug)" class="w-full p-4 bg-slate-50 border border-slate-100 rounded-xl outline-none focus:border-blue-500 text-sm font-bold" required>
                    </div>
                    <input name="target_url" placeholder="Final Destination URL" class="w-full p-4 bg-slate-50 border border-slate-100 rounded-xl outline-none focus:border-blue-500 text-xs" required>
                    
                    <div class="relative">
                        <input name="tag" placeholder="Category (e.g. finance)" class="w-full p-4 bg-blue-50 border border-blue-100 rounded-xl outline-none focus:border-blue-500 text-xs font-bold text-blue-700 placeholder-blue-300">
                        <div class="absolute right-4 top-4 text-[10px] text-blue-300 font-bold">SEO TAG</div>
                    </div>
                    
                    <div class="md:col-span-2">
                        <button class="w-full bg-blue-600 text-white py-4 rounded-xl font-black text-xs uppercase tracking-widest shadow-lg shadow-blue-200 hover:bg-blue-700 transition active:scale-95">Generate SEO Link ⚡</button>
                    </div>
                </form>
            </div>
        </div>

        <!-- 3. CMS / Article Injector -->
        <div class="bg-white p-8 rounded-3xl shadow-sm border border-slate-200 mb-10 relative overflow-hidden">
            <div class="absolute top-0 right-0 p-4 opacity-5">
                <svg class="w-32 h-32" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clip-rule="evenodd"></path></svg>
            </div>
            
            <h2 class="text-sm font-black text-slate-900 mb-6 flex items-center gap-2">
                <span>📝 Content Injection CMS</span>
                <span class="bg-green-100 text-green-700 text-[9px] px-2 py-1 rounded uppercase">Auto-SEO Active</span>
            </h2>

            <form action="/admin/add_article" method="POST" class="space-y-4">
                <div class="flex flex-col md:flex-row gap-4">
                    <input name="title" placeholder="Article Headline (H1)" class="flex-1 p-4 bg-slate-50 border border-slate-100 rounded-xl outline-none focus:border-slate-400 text-sm font-bold" required>
                    <input name="category" placeholder="Category Match" class="w-full md:w-1/4 p-4 bg-slate-50 border border-slate-100 rounded-xl outline-none focus:border-slate-400 text-sm" required>
                </div>
                <textarea name="html_content" placeholder="Paste Article HTML here... (Include <p>, <h2>, <img>). Do NOT include <html> or <body> tags." class="w-full p-4 bg-slate-50 border border-slate-100 rounded-xl outline-none focus:border-slate-400 text-xs font-mono h-48 leading-relaxed" required></textarea>
                <div class="flex justify-end">
                    <button class="bg-slate-900 text-white py-3 px-8 rounded-xl font-bold text-xs uppercase tracking-widest hover:bg-slate-800 transition">Publish & Ping Google</button>
                </div>
            </form>

            <!-- Articles List -->
            <div class="mt-8 border-t border-slate-100 pt-6">
                <h3 class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4">Live Articles</h3>
                <div class="space-y-2 max-h-60 overflow-y-auto pr-2 custom-scroll">
                    {% for art in articles %}
                    <div class="flex justify-between items-center bg-slate-50 p-3 rounded-lg border border-slate-100">
                        <div class="flex items-center gap-3 overflow-hidden">
                            <span class="bg-white border border-slate-200 text-slate-500 text-[10px] font-bold px-2 py-1 rounded uppercase">{{ art.category }}</span>
                            <span class="text-xs font-semibold text-slate-700 truncate">{{ art.title }}</span>
                        </div>
                        <a href="/admin/delete_article/{{ art._id }}" class="text-red-400 hover:text-red-600 transition p-2">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                        </a>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>

        <!-- 4. Link Manager (New Structure) -->
        <div class="space-y-4 pb-20">
            <h2 class="text-xs font-black text-slate-400 uppercase tracking-widest px-2">Active Links & Analytics</h2>
            {% for link in links %}
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 hover:shadow-md transition">
                <div class="flex flex-col md:flex-row justify-between md:items-center gap-4 mb-4">
                    <div>
                        <div class="flex items-center gap-2 mb-1">
                            <span class="font-bold text-slate-800 text-sm">{{ link.title }}</span>
                            {% if link.is_public %}
                            <span class="bg-purple-100 text-purple-600 text-[9px] font-black px-1.5 py-0.5 rounded">PUBLIC</span>
                            {% endif %}
                        </div>
                        <div class="flex items-center gap-3">
                             {% if link.tag %}
                            <span class="text-[10px] font-bold text-blue-600 uppercase bg-blue-50 px-2 py-0.5 rounded">{{ link.tag }}</span>
                            {% endif %}
                            <span class="text-[10px] text-slate-400 font-bold uppercase">Clicks: {{ link.clicks }}</span>
                            <span class="text-[10px] text-slate-300 font-mono">{{ link.slug }}</span>
                        </div>
                    </div>
                    <a href="/admin/delete/{{ link._id }}" class="text-xs font-bold text-red-400 hover:text-red-600 border border-red-100 bg-red-50 px-3 py-2 rounded-lg text-center">Delete Asset</a>
                </div>
                
                <!-- Smart Copy Logic -->
                <div class="flex gap-2">
                    {% if link.tag %}
                        <input id="u_{{ link._id }}" value="{{ host_url }}{{ link.tag }}/{{ link.slug }}" class="flex-1 p-3 bg-slate-50 border border-slate-100 rounded-lg text-[10px] font-mono text-slate-600 outline-none" readonly>
                    {% else %}
                        <input id="u_{{ link._id }}" value="{{ host_url }}v/{{ link.slug }}" class="flex-1 p-3 bg-slate-50 border border-slate-100 rounded-lg text-[10px] font-mono text-slate-600 outline-none" readonly>
                    {% endif %}
                    
                    <button onclick="copy('u_{{ link._id }}')" class="bg-blue-600 hover:bg-blue-700 text-white px-6 rounded-lg text-[10px] font-bold tracking-widest uppercase transition">Copy URL</button>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    <script>
        function copy(id) {
            var c = document.getElementById(id); c.select(); document.execCommand("copy");
            // Optional: Fancy toast notification could go here
            alert("Link copied to clipboard!"); 
        }
    </script>
</body>
</html>
"""
